#!/usr/bin/env python3
"""
仓库更新脚本
独立执行本地Git仓库更新任务

使用方法:
    python update_repos.py
"""

import asyncio
import sys
import os
from datetime import datetime
import logging

# 添加backend目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.project_analyzer import ProjectAnalyzer
from app.config import settings


def setup_logging():
    """设置日志"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('update_repos.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)


async def main():
    """主函数"""
    logger = setup_logging()
    
    print("=" * 60)
    print("🔄 本地仓库更新任务")
    print("=" * 60)
    
    start_time = datetime.now()
    logger.info(f"开始执行仓库更新任务: {start_time}")
    
    try:
        # 检查本地仓库目录
        repos_dir = settings.local_repos_dir
        if not repos_dir or not os.path.exists(repos_dir):
            logger.error(f"本地仓库目录不存在: {repos_dir}")
            print(f"❌ 本地仓库目录不存在: {repos_dir}")
            print("请设置LOCAL_REPOS_DIR环境变量")
            return False
        
        logger.info(f"本地仓库目录: {repos_dir}")
        print(f"📁 本地仓库目录: {repos_dir}")
        
        # 创建分析器实例
        analyzer = ProjectAnalyzer()
        
        # 执行仓库更新
        logger.info("开始更新本地仓库...")
        print("🔄 正在更新本地仓库...")
        
        await analyzer.update_local_repos()
        
        end_time = datetime.now()
        duration = end_time - start_time
        
        logger.info(f"仓库更新任务完成，耗时: {duration}")
        print(f"✅ 仓库更新完成，耗时: {duration}")
        
        return True
        
    except Exception as e:
        logger.error(f"仓库更新任务失败: {e}")
        print(f"❌ 仓库更新失败: {e}")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1) 