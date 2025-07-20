#!/usr/bin/env python3
"""
项目分析脚本
独立执行项目状态分析任务

使用方法:
    python analyze_projects.py
"""

import asyncio
import sys
import os
from datetime import datetime
import logging

# 添加backend目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.project_analyzer import ProjectAnalyzer
from app.database import init_db, db
from app.github_sync import GitHubSync


def setup_logging():
    """设置日志"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('analyze_projects.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)


async def main():
    """主函数"""
    logger = setup_logging()
    
    print("=" * 60)
    print("📊 项目状态分析任务")
    print("=" * 60)
    
    start_time = datetime.now()
    logger.info(f"开始执行项目分析任务: {start_time}")
    
    try:
        # 初始化数据库
        logger.info("初始化数据库...")
        await init_db()
        
        # 创建分析器实例
        analyzer = ProjectAnalyzer()
        
        # 执行项目分析
        logger.info("开始分析项目状态...")
        results = await analyzer.analyze_all_projects()
        
        # 保存分析结果到数据库
        logger.info("保存分析结果到数据库...")
        sync = GitHubSync()
        async with db.get_db() as conn:
            await sync.save_project_statuses(results, conn)
        
        end_time = datetime.now()
        duration = end_time - start_time
        
        # 统计结果
        total_projects = len(results)
        projects_with_readme = sum(1 for r in results.values() if r['structure']['has_readme'])
        avg_quality_score = sum(r['quality_score'] for r in results.values()) / total_projects if total_projects > 0 else 0
        
        logger.info(f"项目分析任务完成，分析了 {total_projects} 个项目，耗时: {duration}")
        print(f"✅ 项目分析完成")
        print(f"📊 分析统计:")
        print(f"   - 总项目数: {total_projects}")
        print(f"   - 有README的项目: {projects_with_readme} ({projects_with_readme/total_projects*100:.1f}%)")
        print(f"   - 平均质量评分: {avg_quality_score:.1f}/100")
        print(f"   - 耗时: {duration}")
        
        return True
        
    except Exception as e:
        logger.error(f"项目分析任务失败: {e}")
        print(f"❌ 项目分析失败: {e}")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1) 