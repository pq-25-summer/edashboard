#!/usr/bin/env python3
"""
检查项目状态数据脚本
"""

import asyncio
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import db


async def check_project_status():
    """检查项目状态数据"""
    print("🔍 检查项目状态数据...")
    
    async with db.get_db() as conn:
        # 检查项目状态表
        async with conn.cursor() as cur:
            await cur.execute("SELECT COUNT(*) as count FROM project_statuses")
            status_count = (await cur.fetchone())["count"]
            print(f"项目状态记录数: {status_count}")
            
            if status_count > 0:
                # 检查第一个项目状态记录
                await cur.execute("""
                    SELECT ps.*, p.name as project_name, p.github_url
                    FROM project_statuses ps
                    JOIN projects p ON ps.project_id = p.id
                    LIMIT 1
                """)
                result = await cur.fetchone()
                if result:
                    print(f"第一个项目状态:")
                    print(f"  - 项目名称: {result['project_name']}")
                    print(f"  - GitHub URL: {result['github_url']}")
                    print(f"  - 质量评分: {result['quality_score']}")
                    print(f"  - 有README: {result['has_readme']}")
            
            # 检查项目表
            await cur.execute("SELECT COUNT(*) as count FROM projects")
            project_count = (await cur.fetchone())["count"]
            print(f"项目记录数: {project_count}")
            
            if project_count > 0:
                # 检查第一个项目记录
                await cur.execute("SELECT * FROM projects LIMIT 1")
                result = await cur.fetchone()
                if result:
                    print(f"第一个项目:")
                    print(f"  - 项目名称: {result['name']}")
                    print(f"  - GitHub URL: {result['github_url']}")
            
            # 检查是否有项目状态但没有对应的项目
            await cur.execute("""
                SELECT COUNT(*) as count 
                FROM project_statuses ps
                LEFT JOIN projects p ON ps.project_id = p.id
                WHERE p.id IS NULL
            """)
            orphan_count = (await cur.fetchone())["count"]
            print(f"孤立项目状态记录数: {orphan_count}")
            
            # 检查所有项目状态记录的github_url
            await cur.execute("""
                SELECT ps.project_id, p.name, p.github_url
                FROM project_statuses ps
                JOIN projects p ON ps.project_id = p.id
                ORDER BY ps.project_id
            """)
            results = await cur.fetchall()
            
            print(f"\n项目状态记录详情:")
            for i, row in enumerate(results[:5]):  # 只显示前5个
                print(f"  {i+1}. 项目ID: {row['project_id']}, 名称: {row['name']}, GitHub: {row['github_url']}")


async def main():
    """主函数"""
    await check_project_status()


if __name__ == "__main__":
    asyncio.run(main()) 