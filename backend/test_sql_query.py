#!/usr/bin/env python3
"""
测试SQL查询脚本
"""

import asyncio
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import db


async def test_sql_query():
    """测试SQL查询"""
    print("🔍 测试SQL查询...")
    
    async with db.get_db() as conn:
        async with conn.cursor() as cur:
            # 测试原始查询
            print("1. 测试原始查询:")
            await cur.execute("""
                SELECT ps.*, p.name as project_name, p.github_url
                FROM project_statuses ps
                JOIN projects p ON ps.project_id = p.id
                ORDER BY ps.quality_score DESC, p.name
                LIMIT 3
            """)
            results = await cur.fetchall()
            
            for i, row in enumerate(results):
                print(f"  记录 {i+1}:")
                print(f"    - project_id: {row['project_id']}")
                print(f"    - project_name: {row['project_name']}")
                print(f"    - github_url: {row['github_url']}")
                print(f"    - quality_score: {row['quality_score']}")
            
            # 检查projects表
            print("\n2. 检查projects表:")
            await cur.execute("SELECT id, name, github_url FROM projects LIMIT 3")
            projects = await cur.fetchall()
            
            for i, project in enumerate(projects):
                print(f"  项目 {i+1}:")
                print(f"    - id: {project['id']}")
                print(f"    - name: {project['name']}")
                print(f"    - github_url: {project['github_url']}")
            
            # 检查project_statuses表
            print("\n3. 检查project_statuses表:")
            await cur.execute("SELECT project_id, quality_score FROM project_statuses LIMIT 3")
            statuses = await cur.fetchall()
            
            for i, status in enumerate(statuses):
                print(f"  状态 {i+1}:")
                print(f"    - project_id: {status['project_id']}")
                print(f"    - quality_score: {status['quality_score']}")
            
            # 测试LEFT JOIN
            print("\n4. 测试LEFT JOIN:")
            await cur.execute("""
                SELECT ps.project_id, p.name as project_name, p.github_url
                FROM project_statuses ps
                LEFT JOIN projects p ON ps.project_id = p.id
                ORDER BY ps.project_id
                LIMIT 3
            """)
            left_join_results = await cur.fetchall()
            
            for i, row in enumerate(left_join_results):
                print(f"  LEFT JOIN 记录 {i+1}:")
                print(f"    - project_id: {row['project_id']}")
                print(f"    - project_name: {row['project_name']}")
                print(f"    - github_url: {row['github_url']}")


async def main():
    """主函数"""
    await test_sql_query()


if __name__ == "__main__":
    asyncio.run(main()) 