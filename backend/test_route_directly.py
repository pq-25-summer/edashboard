#!/usr/bin/env python3
"""
直接测试API路由
"""

import asyncio
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.routers.project_status import _get_all_project_statuses_internal
from app.database import db


async def test_route_directly():
    """直接测试路由函数"""
    print("🔍 直接测试API路由...")
    
    try:
        # 直接调用内部函数
        async with db.get_db() as conn:
            result = await _get_all_project_statuses_internal(conn)
        
        print(f"路由返回结果数量: {len(result)}")
        if result:
            first_item = result[0]
            print(f"第一个项目:")
            print(f"  - project_name: {first_item.get('project_name')}")
            print(f"  - github_url: {first_item.get('github_url')}")
            print(f"  - project_id: {first_item.get('project_id')}")
            print(f"  - quality_score: {first_item.get('quality_score')}")
        
        return result
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
        return None


async def main():
    """主函数"""
    await test_route_directly()


if __name__ == "__main__":
    asyncio.run(main()) 