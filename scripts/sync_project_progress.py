#!/usr/bin/env python3
"""
项目进度数据同步脚本
从本地Git仓库和GitHub API收集项目进度数据
"""

import os
import sys
import asyncio
import argparse
import logging
from datetime import datetime, timedelta
from pathlib import Path
import subprocess
import json
from typing import Dict, List, Any, Optional

# 添加backend目录到Python路径
backend_path = Path(__file__).parent.parent / 'backend'
sys.path.insert(0, str(backend_path))

from app.database import db
from app.config import settings
import psycopg
from psycopg.rows import dict_row

# 配置日志
project_root = Path(__file__).parent.parent
logs_dir = project_root / 'logs'
logs_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(logs_dir / 'project_progress_sync.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class ProjectProgressSync:
    def __init__(self):
        self.local_repos_dir = settings.local_repos_dir
        self.start_date = datetime(2025, 7, 9).date()
        self.end_date = self.start_date + timedelta(weeks=5)
        
    async def sync_all_projects(self, dry_run: bool = False):
        """同步所有项目的进度数据"""
        logger.info("开始同步项目进度数据...")
        logger.info(f"跟踪时间范围: {self.start_date} 到 {self.end_date}")
        
        try:
            async with db.get_db() as conn:
                # 获取所有项目
                async with conn.cursor() as cur:
                    await cur.execute("SELECT id, name, github_url FROM projects")
                    projects = await cur.fetchall()
                
                logger.info(f"找到 {len(projects)} 个项目")
                
                for project in projects:
                    logger.info(f"处理项目: {project['name']}")
                    await self.sync_project_progress(
                        conn, project, dry_run
                    )
                
                logger.info("项目进度数据同步完成")
                
        except Exception as e:
            logger.error(f"同步过程中出现错误: {e}")
            raise
    
    async def sync_project_progress(
        self, 
        conn: psycopg.AsyncConnection, 
        project: Dict[str, Any], 
        dry_run: bool = False
    ):
        """同步单个项目的进度数据"""
        project_id = project['id']
        project_name = project['name']
        github_url = project['github_url']
        
        try:
            # 从GitHub URL提取owner/repo
            owner, repo = self.extract_owner_repo(github_url)
            if not owner or not repo:
                logger.warning(f"无法解析GitHub URL: {github_url}")
                return
            
            # 构建本地仓库路径
            local_repo_path = Path(self.local_repos_dir) / owner / repo
            
            if not local_repo_path.exists():
                logger.warning(f"本地仓库不存在: {local_repo_path}")
                return
            
            # 获取Git提交数据
            commit_data = await self.get_git_commit_data(local_repo_path)
            
            # 获取GitHub Issues数据
            issues_data = await self.get_github_issues_data(owner, repo)
            
            # 合并数据并保存到数据库
            if not dry_run:
                await self.save_project_progress(
                    conn, project_id, commit_data, issues_data
                )
            else:
                logger.info(f"[DRY RUN] 项目 {project_name} 的数据:")
                logger.info(f"  提交数据: {len(commit_data)} 条记录")
                logger.info(f"  Issues数据: {len(issues_data)} 条记录")
                
        except Exception as e:
            logger.error(f"同步项目 {project_name} 时出错: {e}")
    
    def extract_owner_repo(self, github_url: str) -> tuple[Optional[str], Optional[str]]:
        """从GitHub URL提取owner和repo名称"""
        try:
            # 处理不同的GitHub URL格式
            if github_url.startswith('https://github.com/'):
                parts = github_url.replace('https://github.com/', '').split('/')
            elif github_url.startswith('git@github.com:'):
                parts = github_url.replace('git@github.com:', '').replace('.git', '').split('/')
            else:
                return None, None
            
            if len(parts) >= 2:
                return parts[0], parts[1]
            return None, None
        except Exception:
            return None, None
    
    async def get_git_commit_data(self, repo_path: Path) -> List[Dict[str, Any]]:
        """从Git仓库获取提交数据"""
        commit_data = []
        
        try:
            # 切换到仓库目录
            os.chdir(repo_path)
            
            # 获取指定日期范围内的提交
            cmd = [
                'git', 'log',
                '--since', self.start_date.isoformat(),
                '--until', (self.end_date + timedelta(days=1)).isoformat(),
                '--format=format:%H|%an|%ad|%s',
                '--date=short',
                '--numstat'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=repo_path)
            
            if result.returncode != 0:
                logger.warning(f"Git命令执行失败: {result.stderr}")
                return commit_data
            
            # 解析Git输出
            lines = result.stdout.strip().split('\n')
            i = 0
            while i < len(lines):
                line = lines[i].strip()
                if not line:
                    i += 1
                    continue
                
                # 解析提交信息
                if '|' in line:
                    commit_parts = line.split('|')
                    if len(commit_parts) >= 4:
                        commit_hash = commit_parts[0]
                        author = commit_parts[1]
                        date_str = commit_parts[2]
                        message = commit_parts[3]
                        
                        # 解析文件统计信息
                        lines_added = 0
                        lines_deleted = 0
                        files_changed = 0
                        
                        i += 1
                        while i < len(lines) and lines[i].strip() and not '|' in lines[i]:
                            stat_line = lines[i].strip()
                            if stat_line and stat_line[0].isdigit():
                                parts = stat_line.split('\t')
                                if len(parts) >= 2:
                                    try:
                                        added = int(parts[0]) if parts[0] != '-' else 0
                                        deleted = int(parts[1]) if parts[1] != '-' else 0
                                        lines_added += added
                                        lines_deleted += deleted
                                        files_changed += 1
                                    except ValueError:
                                        pass
                            i += 1
                        
                        # 按日期分组
                        commit_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                        if self.start_date <= commit_date <= self.end_date:
                            commit_data.append({
                                'date': commit_date.isoformat(),
                                'commit_hash': commit_hash,
                                'author': author,
                                'message': message,
                                'lines_added': lines_added,
                                'lines_deleted': lines_deleted,
                                'files_changed': files_changed
                            })
                else:
                    i += 1
            
            # 按日期聚合数据
            daily_commits = {}
            for commit in commit_data:
                date = commit['date']
                if date not in daily_commits:
                    daily_commits[date] = {
                        'date': date,
                        'has_commit': True,
                        'commit_count': 0,
                        'lines_added': 0,
                        'lines_deleted': 0,
                        'files_changed': 0
                    }
                
                daily_commits[date]['commit_count'] += 1
                daily_commits[date]['lines_added'] += commit['lines_added']
                daily_commits[date]['lines_deleted'] += commit['lines_deleted']
                daily_commits[date]['files_changed'] += commit['files_changed']
            
            return list(daily_commits.values())
            
        except Exception as e:
            logger.error(f"获取Git提交数据时出错: {e}")
            return commit_data
    
    async def get_github_issues_data(self, owner: str, repo: str) -> List[Dict[str, Any]]:
        """从GitHub API获取Issues数据"""
        issues_data = []
        
        try:
            # 使用GitHub CLI获取Issues数据
            cmd = [
                'gh', 'api', f'repos/{owner}/{repo}/issues',
                '--jq', '.[] | {number: .number, title: .title, state: .state, created_at: .created_at, closed_at: .closed_at, comments: .comments}'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.warning(f"GitHub API调用失败: {result.stderr}")
                return issues_data
            
            # 解析JSON输出
            lines = result.stdout.strip().split('\n')
            for line in lines:
                if line.strip():
                    try:
                        issue = json.loads(line)
                        created_date = datetime.fromisoformat(issue['created_at'].replace('Z', '+00:00')).date()
                        
                        if self.start_date <= created_date <= self.end_date:
                            issues_data.append({
                                'date': created_date.isoformat(),
                                'number': issue['number'],
                                'title': issue['title'],
                                'state': issue['state'],
                                'created_at': issue['created_at'],
                                'closed_at': issue.get('closed_at'),
                                'comments': issue['comments']
                            })
                    except json.JSONDecodeError:
                        continue
            
            # 按日期聚合数据
            daily_issues = {}
            for issue in issues_data:
                date = issue['date']
                if date not in daily_issues:
                    daily_issues[date] = {
                        'date': date,
                        'issues_created': 0,
                        'issues_closed': 0,
                        'issues_commented': 0
                    }
                
                daily_issues[date]['issues_created'] += 1
                if issue['state'] == 'closed' and issue.get('closed_at'):
                    closed_date = datetime.fromisoformat(issue['closed_at'].replace('Z', '+00:00')).date()
                    if self.start_date <= closed_date <= self.end_date:
                        closed_date_str = closed_date.isoformat()
                        if closed_date_str not in daily_issues:
                            daily_issues[closed_date_str] = {
                                'date': closed_date_str,
                                'issues_created': 0,
                                'issues_closed': 0,
                                'issues_commented': 0
                            }
                        daily_issues[closed_date_str]['issues_closed'] += 1
                
                if issue['comments'] > 0:
                    daily_issues[date]['issues_commented'] += issue['comments']
            
            return list(daily_issues.values())
            
        except Exception as e:
            logger.error(f"获取GitHub Issues数据时出错: {e}")
            return issues_data
    
    async def save_project_progress(
        self, 
        conn: psycopg.AsyncConnection, 
        project_id: int, 
        commit_data: List[Dict[str, Any]], 
        issues_data: List[Dict[str, Any]]
    ):
        """保存项目进度数据到数据库"""
        try:
            # 合并提交和Issues数据
            progress_data = {}
            
            # 初始化所有日期的数据
            current_date = self.start_date
            while current_date <= self.end_date:
                date_str = current_date.isoformat()
                progress_data[date_str] = {
                    'project_id': project_id,
                    'date': date_str,
                    'has_commit': False,
                    'commit_count': 0,
                    'lines_added': 0,
                    'lines_deleted': 0,
                    'files_changed': 0,
                    'issues_created': 0,
                    'issues_closed': 0,
                    'issues_commented': 0
                }
                current_date += timedelta(days=1)
            
            # 合并提交数据
            for commit in commit_data:
                date = commit['date']
                if date in progress_data:
                    progress_data[date].update({
                        'has_commit': True,
                        'commit_count': commit['commit_count'],
                        'lines_added': commit['lines_added'],
                        'lines_deleted': commit['lines_deleted'],
                        'files_changed': commit['files_changed']
                    })
            
            # 合并Issues数据
            for issue in issues_data:
                date = issue['date']
                if date in progress_data:
                    progress_data[date].update({
                        'issues_created': issue['issues_created'],
                        'issues_closed': issue['issues_closed'],
                        'issues_commented': issue['issues_commented']
                    })
            
            # 保存到数据库
            async with conn.cursor() as cur:
                for date_str, data in progress_data.items():
                    await cur.execute("""
                        INSERT INTO project_progress (
                            project_id, date, has_commit, commit_count, 
                            lines_added, lines_deleted, files_changed,
                            issues_created, issues_closed, issues_commented
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (project_id, date) 
                        DO UPDATE SET
                            has_commit = EXCLUDED.has_commit,
                            commit_count = EXCLUDED.commit_count,
                            lines_added = EXCLUDED.lines_added,
                            lines_deleted = EXCLUDED.lines_deleted,
                            files_changed = EXCLUDED.files_changed,
                            issues_created = EXCLUDED.issues_created,
                            issues_closed = EXCLUDED.issues_closed,
                            issues_commented = EXCLUDED.issues_commented,
                            updated_at = CURRENT_TIMESTAMP
                    """, (
                        data['project_id'], data['date'], data['has_commit'],
                        data['commit_count'], data['lines_added'], data['lines_deleted'],
                        data['files_changed'], data['issues_created'], data['issues_closed'],
                        data['issues_commented']
                    ))
            
            await conn.commit()
            logger.info(f"项目 {project_id} 的进度数据已保存")
            
        except Exception as e:
            logger.error(f"保存项目进度数据时出错: {e}")
            await conn.rollback()
            raise


async def main():
    parser = argparse.ArgumentParser(description='同步项目进度数据')
    parser.add_argument('--dry-run', action='store_true', help='试运行模式，不保存数据')
    parser.add_argument('--project-id', type=int, help='只同步指定项目ID')
    
    args = parser.parse_args()
    
    # 确保日志目录存在
    os.makedirs('logs', exist_ok=True)
    
    sync = ProjectProgressSync()
    
    if args.dry_run:
        logger.info("运行在试运行模式")
    
    try:
        await sync.sync_all_projects(dry_run=args.dry_run)
        logger.info("同步完成")
    except Exception as e:
        logger.error(f"同步失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main()) 