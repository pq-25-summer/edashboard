#!/usr/bin/env python3
"""
测试API中的数据库连接
"""

import asyncio
import sys
import os
from contextlib import asynccontextmanager

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import get_db


async def test_api_db_connection():
    """测试API中的数据库连接"""
    print("🔍 测试API中的数据库连接...")
    
    # 模拟API中的数据库连接
    async for db in get_db():
        async with db.cursor() as cur:
            # 测试原始查询
            print("1. 测试API中的查询:")
            await cur.execute("""
                SELECT ps.*, p.name as project_name, p.github_url
                FROM project_statuses ps
                JOIN projects p ON ps.project_id = p.id
                ORDER BY ps.quality_score DESC, p.name
                LIMIT 3
            """)
            results = await cur.fetchall()
            
            print(f"查询结果数量: {len(results)}")
            for i, row in enumerate(results):
                print(f"  记录 {i+1}:")
                print(f"    - project_id: {row['project_id']}")
                print(f"    - project_name: {row['project_name']}")
                print(f"    - github_url: {row['github_url']}")
                print(f"    - quality_score: {row['quality_score']}")
        
        break  # 只执行一次


async def main():
    """主函数"""
    await test_api_db_connection()


if __name__ == "__main__":
    asyncio.run(main()) 