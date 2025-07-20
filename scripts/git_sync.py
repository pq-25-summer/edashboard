#!/usr/bin/env python3
"""
Git仓库同步程序
专门负责更新所有本地仓库，不阻塞其他分析任务
"""

import asyncio
import sys
import os
import subprocess
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

# 添加backend目录到Python路径
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backend'))

from app.config import settings
from app.database import db, init_db


def setup_logging():
    """设置日志"""
    # 确保日志目录存在
    os.makedirs('logs', exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/git_sync.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)


async def get_projects_from_db() -> List[Dict[str, Any]]:
    """从数据库获取项目列表"""
    async with db.get_db() as conn:
        async with conn.cursor() as cur:
            await cur.execute("SELECT id, name, github_url FROM projects")
            projects = await cur.fetchall()
            return projects


def get_repo_path(github_url: str) -> str:
    """从GitHub URL获取本地仓库路径"""
    # 从URL中提取owner/repo格式
    if github_url.startswith('https://github.com/'):
        repo_part = github_url.replace('https://github.com/', '').rstrip('/')
    elif github_url.startswith('git@github.com:'):
        repo_part = github_url.replace('git@github.com:', '').replace('.git', '')
    else:
        repo_part = github_url
    
    # 构建本地路径
    return os.path.join(settings.local_repos_dir, repo_part)


async def sync_single_repo(repo_path: str, project_name: str, logger) -> Dict[str, Any]:
    """同步单个仓库"""
    result = {
        'repo_path': repo_path,
        'project_name': project_name,
        'success': False,
        'error': None,
        'changes': False,
        'last_commit': None,
        'branch': None
    }
    
    try:
        if not os.path.exists(repo_path):
            logger.warning(f"仓库不存在: {repo_path}")
            result['error'] = "仓库不存在"
            return result
        
        # 获取当前分支
        branch_result = subprocess.run(
            ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
            cwd=repo_path,
            capture_output=True,
            text=True
        )
        if branch_result.returncode == 0:
            result['branch'] = branch_result.stdout.strip()
        
        # 获取当前提交
        commit_result = subprocess.run(
            ['git', 'rev-parse', 'HEAD'],
            cwd=repo_path,
            capture_output=True,
            text=True
        )
        if commit_result.returncode == 0:
            result['last_commit'] = commit_result.stdout.strip()
        
        # 检查是否有未提交的更改
        status_result = subprocess.run(
            ['git', 'status', '--porcelain'],
            cwd=repo_path,
            capture_output=True,
            text=True
        )
        has_changes = bool(status_result.stdout.strip())
        
        if has_changes:
            logger.warning(f"仓库有未提交的更改: {repo_path}")
            result['error'] = "有未提交的更改"
            return result
        
        # 执行git pull
        logger.info(f"正在同步仓库: {project_name} ({repo_path})")
        
        # 先获取远程更新信息
        fetch_result = subprocess.run(
            ['git', 'fetch', 'origin'],
            cwd=repo_path,
            capture_output=True,
            text=True
        )
        
        if fetch_result.returncode != 0:
            logger.error(f"获取远程更新失败: {project_name}")
            result['error'] = f"fetch失败: {fetch_result.stderr}"
            return result
        
        # 检查是否有更新
        log_result = subprocess.run(
            ['git', 'log', 'HEAD..origin/main', '--oneline'],
            cwd=repo_path,
            capture_output=True,
            text=True
        )
        
        has_updates = bool(log_result.stdout.strip())
        
        if has_updates:
            # 执行pull
            pull_result = subprocess.run(
                ['git', 'pull', 'origin', 'main'],
                cwd=repo_path,
                capture_output=True,
                text=True
            )
            
            if pull_result.returncode == 0:
                logger.info(f"✅ 仓库同步成功: {project_name}")
                result['success'] = True
                result['changes'] = True
                
                # 更新最后提交信息
                new_commit_result = subprocess.run(
                    ['git', 'rev-parse', 'HEAD'],
                    cwd=repo_path,
                    capture_output=True,
                    text=True
                )
                if new_commit_result.returncode == 0:
                    result['last_commit'] = new_commit_result.stdout.strip()
            else:
                logger.error(f"❌ 仓库同步失败: {project_name}")
                result['error'] = f"pull失败: {pull_result.stderr}"
        else:
            logger.info(f"✅ 仓库已是最新: {project_name}")
            result['success'] = True
            result['changes'] = False
        
    except Exception as e:
        logger.error(f"❌ 同步仓库时出错 {project_name}: {e}")
        result['error'] = str(e)
    
    return result


async def update_sync_status(sync_results: List[Dict[str, Any]], logger):
    """更新同步状态到数据库"""
    try:
        async with db.get_db() as conn:
            async with conn.cursor() as cur:
                # 创建同步记录表（如果不存在）
                await cur.execute("""
                    CREATE TABLE IF NOT EXISTS git_sync_logs (
                        id SERIAL PRIMARY KEY,
                        sync_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        total_projects INTEGER,
                        successful_syncs INTEGER,
                        failed_syncs INTEGER,
                        projects_with_changes INTEGER,
                        sync_duration_seconds DECIMAL(10,2),
                        details JSONB
                    )
                """)
                
                # 统计结果
                total_projects = len(sync_results)
                successful_syncs = sum(1 for r in sync_results if r['success'])
                failed_syncs = total_projects - successful_syncs
                projects_with_changes = sum(1 for r in sync_results if r.get('changes', False))
                
                # 保存同步记录
                await cur.execute("""
                    INSERT INTO git_sync_logs (
                        total_projects, successful_syncs, failed_syncs,
                        projects_with_changes, details
                    ) VALUES (%s, %s, %s, %s, %s)
                """, (
                    total_projects,
                    successful_syncs,
                    failed_syncs,
                    projects_with_changes,
                    json.dumps(sync_results)
                ))
                
                await conn.commit()
                
                logger.info(f"📊 同步统计: 成功 {successful_syncs}/{total_projects}, 有更新 {projects_with_changes}")
                
    except Exception as e:
        logger.error(f"更新同步状态失败: {e}")


async def main():
    """主函数"""
    logger = setup_logging()
    
    print("=" * 60)
    print("🔄 Git仓库同步程序")
    print("=" * 60)
    
    start_time = datetime.now()
    logger.info(f"开始Git同步任务: {start_time}")
    
    try:
        # 确保日志目录存在
        os.makedirs('logs', exist_ok=True)
        
        # 初始化数据库
        await init_db()
        
        # 获取项目列表
        projects = await get_projects_from_db()
        logger.info(f"找到 {len(projects)} 个项目需要同步")
        
        if not projects:
            logger.warning("没有找到需要同步的项目")
            return
        
        # 同步所有仓库
        sync_results = []
        for project in projects:
            repo_path = get_repo_path(project['github_url'])
            result = await sync_single_repo(repo_path, project['name'], logger)
            sync_results.append(result)
            
            # 添加短暂延迟，避免过于频繁的git操作
            await asyncio.sleep(0.5)
        
        # 更新同步状态
        await update_sync_status(sync_results, logger)
        
        end_time = datetime.now()
        duration = end_time - start_time
        
        logger.info(f"Git同步任务完成，耗时: {duration}")
        
        # 显示摘要
        successful = sum(1 for r in sync_results if r['success'])
        with_changes = sum(1 for r in sync_results if r.get('changes', False))
        
        print(f"\n📊 同步摘要:")
        print(f"   - 总项目数: {len(projects)}")
        print(f"   - 同步成功: {successful}")
        print(f"   - 同步失败: {len(projects) - successful}")
        print(f"   - 有更新: {with_changes}")
        print(f"   - 耗时: {duration}")
        
        if with_changes > 0:
            print(f"\n🔄 建议: 有 {with_changes} 个项目有更新，可以运行分析任务")
        
    except Exception as e:
        logger.error(f"Git同步任务失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main()) 