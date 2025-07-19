#!/usr/bin/env python3
"""
GitHub数据同步脚本
独立执行GitHub项目数据同步任务

使用方法:
    python sync_data.py
"""

import asyncio
import sys
import os
from datetime import datetime
import logging

# 添加backend目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.github_sync import GitHubSync
from app.database import init_db
from app.config import settings


def setup_logging():
    """设置日志"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('sync_data.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)


async def main():
    """主函数"""
    logger = setup_logging()
    
    print("=" * 60)
    print("🔄 GitHub数据同步任务")
    print("=" * 60)
    
    start_time = datetime.now()
    logger.info(f"开始执行数据同步任务: {start_time}")
    
    try:
        # 检查环境变量
        if not settings.github_token:
            logger.error("错误: 未设置GitHub token")
            print("❌ 请设置GITHUB_TOKEN环境变量")
            return False
        
        # 初始化数据库
        logger.info("初始化数据库...")
        await init_db()
        
        # 创建同步器实例
        sync = GitHubSync()
        
        # 执行完整同步
        logger.info("开始执行GitHub数据同步...")
        await sync.sync_all_projects()
        
        end_time = datetime.now()
        duration = end_time - start_time
        
        logger.info(f"数据同步任务完成，耗时: {duration}")
        print(f"✅ 数据同步完成，耗时: {duration}")
        
        return True
        
    except Exception as e:
        logger.error(f"数据同步任务失败: {e}")
        print(f"❌ 数据同步失败: {e}")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1) 