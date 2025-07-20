#!/usr/bin/env python3
"""
统一命令行工具
提供所有后台任务的统一接口

使用方法:
    python cli.py sync      # 执行完整同步
    python cli.py analyze   # 仅执行分析
    python cli.py update    # 仅更新仓库
    python cli.py status    # 查看状态
"""

import asyncio
import sys
import os
import argparse
from datetime import datetime
import logging

# 添加backend目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.database import init_db, db
from app.github_sync import GitHubSync
from app.project_analyzer import ProjectAnalyzer


def setup_logging():
    """设置日志"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('cli.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)


async def run_sync():
    """执行完整数据同步"""
    logger = setup_logging()
    
    print("🔄 执行完整数据同步...")
    logger.info("开始执行完整数据同步")
    
    try:
        await init_db()
        sync = GitHubSync()
        await sync.sync_all_projects()
        
        logger.info("完整数据同步完成")
        print("✅ 完整数据同步完成")
        return True
        
    except Exception as e:
        logger.error(f"完整数据同步失败: {e}")
        print(f"❌ 完整数据同步失败: {e}")
        return False


async def run_analyze():
    """仅执行项目分析"""
    logger = setup_logging()
    
    print("📊 执行项目分析...")
    logger.info("开始执行项目分析")
    
    try:
        await init_db()
        analyzer = ProjectAnalyzer()
        results = await analyzer.analyze_all_projects()
        
        # 保存结果
        sync = GitHubSync()
        async with db.get_db() as conn:
            await sync.save_project_statuses(results, conn)
        
        logger.info(f"项目分析完成，分析了 {len(results)} 个项目")
        print(f"✅ 项目分析完成，分析了 {len(results)} 个项目")
        return True
        
    except Exception as e:
        logger.error(f"项目分析失败: {e}")
        print(f"❌ 项目分析失败: {e}")
        return False


async def run_git_sync():
    """同步Git仓库"""
    logger = setup_logging()
    
    print("🔄 同步Git仓库...")
    logger.info("开始同步Git仓库")
    
    try:
        # 运行git同步脚本
        import subprocess
        result = subprocess.run([
            sys.executable, 'scripts/git_sync.py'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info("Git仓库同步完成")
            print("✅ Git仓库同步完成")
            print(result.stdout)
            return True
        else:
            logger.error(f"Git仓库同步失败: {result.stderr}")
            print(f"❌ Git仓库同步失败: {result.stderr}")
            return False
        
    except Exception as e:
        logger.error(f"Git同步失败: {e}")
        print(f"❌ Git同步失败: {e}")
        return False


async def run_tech_stack():
    """保存技术栈数据"""
    logger = setup_logging()
    
    print("💾 保存技术栈数据...")
    logger.info("开始保存技术栈数据")
    
    try:
        # 运行技术栈保存脚本
        import subprocess
        result = subprocess.run([
            sys.executable, 'scripts/save_tech_stack.py'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info("技术栈数据保存完成")
            print("✅ 技术栈数据保存完成")
            print(result.stdout)
            return True
        else:
            logger.error(f"技术栈数据保存失败: {result.stderr}")
            print(f"❌ 技术栈数据保存失败: {result.stderr}")
            return False
        
    except Exception as e:
        logger.error(f"技术栈数据保存失败: {e}")
        print(f"❌ 技术栈数据保存失败: {e}")
        return False


async def run_issue_driven_analysis():
    """执行Issue驱动开发分析"""
    logger = setup_logging()
    
    print("🔍 执行Issue驱动开发分析...")
    logger.info("开始执行Issue驱动开发分析")
    
    try:
        # 运行Issue驱动开发分析脚本
        import subprocess
        result = subprocess.run([
            sys.executable, 'scripts/analyze_issue_driven_development.py',
            '--repos-path', '/Users/mars/jobs/pq/repos'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info("Issue驱动开发分析完成")
            print("✅ Issue驱动开发分析完成")
            print(result.stdout)
            return True
        else:
            logger.error(f"Issue驱动开发分析失败: {result.stderr}")
            print(f"❌ Issue驱动开发分析失败: {result.stderr}")
            return False
        
    except Exception as e:
        logger.error(f"Issue驱动开发分析失败: {e}")
        print(f"❌ Issue驱动开发分析失败: {e}")
        return False


async def run_issue_driven_sync():
    """同步Issue驱动开发数据"""
    logger = setup_logging()
    
    print("🔄 同步Issue驱动开发数据...")
    logger.info("开始同步Issue驱动开发数据")
    
    try:
        # 运行Issue驱动开发数据同步脚本
        import subprocess
        result = subprocess.run([
            sys.executable, 'scripts/sync_issue_driven_data.py'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info("Issue驱动开发数据同步完成")
            print("✅ Issue驱动开发数据同步完成")
            print(result.stdout)
            return True
        else:
            logger.error(f"Issue驱动开发数据同步失败: {result.stderr}")
            print(f"❌ Issue驱动开发数据同步失败: {result.stderr}")
            return False
        
    except Exception as e:
        logger.error(f"Issue驱动开发数据同步失败: {e}")
        print(f"❌ Issue驱动开发数据同步失败: {e}")
        return False


async def run_project_progress_sync():
    """同步项目进度数据"""
    logger = setup_logging()
    
    print("📅 同步项目进度数据...")
    logger.info("开始同步项目进度数据")
    
    try:
        # 运行项目进度数据同步脚本
        import subprocess
        result = subprocess.run([
            sys.executable, 'scripts/sync_project_progress.py'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info("项目进度数据同步完成")
            print("✅ 项目进度数据同步完成")
            print(result.stdout)
            return True
        else:
            logger.error(f"项目进度数据同步失败: {result.stderr}")
            print(f"❌ 项目进度数据同步失败: {result.stderr}")
            return False
        
    except Exception as e:
        logger.error(f"项目进度数据同步失败: {e}")
        print(f"❌ 项目进度数据同步失败: {e}")
        return False


async def run_project_progress_sync_dry_run():
    """试运行项目进度数据同步"""
    logger = setup_logging()
    
    print("🧪 试运行项目进度数据同步...")
    logger.info("开始试运行项目进度数据同步")
    
    try:
        # 运行项目进度数据同步脚本（试运行模式）
        import subprocess
        result = subprocess.run([
            sys.executable, 'scripts/sync_project_progress.py', '--dry-run'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info("项目进度数据同步试运行完成")
            print("✅ 项目进度数据同步试运行完成")
            print(result.stdout)
            return True
        else:
            logger.error(f"项目进度数据同步试运行失败: {result.stderr}")
            print(f"❌ 项目进度数据同步试运行失败: {result.stderr}")
            return False
        
    except Exception as e:
        logger.error(f"项目进度数据同步试运行失败: {e}")
        print(f"❌ 项目进度数据同步试运行失败: {e}")
        return False


async def show_status():
    """显示系统状态"""
    logger = setup_logging()
    
    print("📊 系统状态")
    print("=" * 40)
    
    try:
        await init_db()
        
        # 获取数据库统计
        async with db.get_db() as conn:
            async with conn.cursor() as cur:
                # 项目数量
                await cur.execute("SELECT COUNT(*) FROM projects")
                project_count = (await cur.fetchone())["count"]
                
                # 学生数量
                await cur.execute("SELECT COUNT(*) FROM students")
                student_count = (await cur.fetchone())["count"]
                
                # 提交数量
                await cur.execute("SELECT COUNT(*) FROM commits")
                commit_count = (await cur.fetchone())["count"]
                
                # Issue数量
                await cur.execute("SELECT COUNT(*) FROM issues")
                issue_count = (await cur.fetchone())["count"]
                
                # 项目状态数量
                await cur.execute("SELECT COUNT(*) FROM project_statuses")
                status_count = (await cur.fetchone())["count"]
                
                # Issue驱动开发统计
                await cur.execute("""
                    SELECT 
                        COUNT(CASE WHEN uses_issue_driven_development THEN 1 END) as projects_with_issue_driven,
                        AVG(issue_driven_score) as avg_issue_driven_score,
                        AVG(commit_issue_ratio) as avg_commit_issue_ratio
                    FROM project_statuses
                """)
                issue_driven_stats = await cur.fetchone()
                
                # 项目进度统计
                await cur.execute("""
                    SELECT 
                        COUNT(DISTINCT project_id) as projects_with_progress,
                        SUM(commit_count) as total_commits,
                        SUM(lines_added) as total_lines_added,
                        SUM(issues_created) as total_issues_created,
                        SUM(issues_closed) as total_issues_closed,
                        COUNT(DISTINCT date) as tracking_days
                    FROM project_progress
                """)
                progress_stats = await cur.fetchone()
                
                # 最近更新时间
                await cur.execute("SELECT MAX(updated_at) FROM project_statuses")
                last_update_result = await cur.fetchone()
                last_update = last_update_result["max"] if last_update_result["max"] else None
        
        print(f"📊 数据统计:")
        print(f"   - 项目数量: {project_count}")
        print(f"   - 学生数量: {student_count}")
        print(f"   - 提交数量: {commit_count}")
        print(f"   - Issue数量: {issue_count}")
        print(f"   - 项目状态记录: {status_count}")
        
        print(f"📋 Issue驱动开发:")
        print(f"   - 使用Issue驱动开发: {issue_driven_stats['projects_with_issue_driven']} ({issue_driven_stats['projects_with_issue_driven']/project_count*100:.1f}%)")
        print(f"   - 平均评分: {issue_driven_stats['avg_issue_driven_score']:.1f}/100")
        print(f"   - 平均提交-Issue关联率: {issue_driven_stats['avg_commit_issue_ratio']:.1f}%")
        
        print(f"📅 项目进度跟踪:")
        print(f"   - 有进度数据的项目: {progress_stats['projects_with_progress']} ({progress_stats['projects_with_progress']/project_count*100:.1f}%)")
        print(f"   - 总提交数: {progress_stats['total_commits']}")
        print(f"   - 总代码行数: {progress_stats['total_lines_added']}")
        print(f"   - 总Issue创建: {progress_stats['total_issues_created']}")
        print(f"   - 总Issue关闭: {progress_stats['total_issues_closed']}")
        print(f"   - 跟踪天数: {progress_stats['tracking_days']}")
        
        if last_update:
            print(f"   - 最后更新时间: {last_update}")
        else:
            print(f"   - 最后更新时间: 无")
        
        return True
        
    except Exception as e:
        logger.error(f"获取状态失败: {e}")
        print(f"❌ 获取状态失败: {e}")
        return False


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="软件工程课看板系统 - 统一命令行工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  python cli.py sync                    # 执行完整数据同步
  python cli.py analyze                 # 仅执行项目分析
  python cli.py git-sync                # 同步Git仓库
  python cli.py tech-stack              # 保存技术栈数据
  python cli.py status                  # 查看系统状态
  python cli.py issue-driven-analysis   # 执行Issue驱动开发分析
  python cli.py issue-driven-sync       # 同步Issue驱动开发数据
  python cli.py project-progress-sync   # 同步项目进度数据
  python cli.py project-progress-dry-run # 试运行项目进度数据同步
        """
    )
    
    parser.add_argument(
        'command',
        choices=['sync', 'analyze', 'git-sync', 'tech-stack', 'status', 'issue-driven-analysis', 'issue-driven-sync', 'project-progress-sync', 'project-progress-dry-run'],
        help='要执行的命令'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='显示详细日志'
    )
    
    args = parser.parse_args()
    
    # 设置日志级别
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    print("=" * 60)
    print("🔧 软件工程课看板系统 - 命令行工具")
    print("=" * 60)
    
    # 执行命令
    if args.command == 'sync':
        success = asyncio.run(run_sync())
    elif args.command == 'analyze':
        success = asyncio.run(run_analyze())
    elif args.command == 'git-sync':
        success = asyncio.run(run_git_sync())
    elif args.command == 'tech-stack':
        success = asyncio.run(run_tech_stack())
    elif args.command == 'status':
        success = asyncio.run(show_status())
    elif args.command == 'issue-driven-analysis':
        success = asyncio.run(run_issue_driven_analysis())
    elif args.command == 'issue-driven-sync':
        success = asyncio.run(run_issue_driven_sync())
    elif args.command == 'project-progress-sync':
        success = asyncio.run(run_project_progress_sync())
    elif args.command == 'project-progress-dry-run':
        success = asyncio.run(run_project_progress_sync_dry_run())
    else:
        print(f"❌ 未知命令: {args.command}")
        return 1
    
    print("=" * 60)
    if success:
        print("✅ 命令执行成功")
        return 0
    else:
        print("❌ 命令执行失败")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 