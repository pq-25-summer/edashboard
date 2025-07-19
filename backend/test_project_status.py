#!/usr/bin/env python3
"""
项目状态功能测试脚本
"""

import asyncio
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.project_analyzer import ProjectAnalyzer
from app.github_sync import GitHubSync
from app.database import init_db


async def test_project_analyzer():
    """测试项目分析器"""
    print("🔍 测试项目分析器...")
    
    analyzer = ProjectAnalyzer()
    
    # 测试更新本地仓库
    print("  更新本地仓库...")
    success = await analyzer.update_local_repos()
    print(f"  更新结果: {'成功' if success else '失败'}")
    
    # 测试项目分析
    print("  分析项目状态...")
    results = await analyzer.analyze_all_projects()
    print(f"  分析完成，共 {len(results)} 个项目")
    
    # 显示前3个项目的分析结果
    for i, (project_key, data) in enumerate(list(results.items())[:3]):
        print(f"  项目 {i+1}: {project_key}")
        print(f"    - 质量评分: {data['quality_score']}/100")
        print(f"    - 主要语言: {data['structure']['main_language']}")
        print(f"    - 文件数: {data['structure']['total_files']}")
        print(f"    - 提交数: {data['git_info']['commit_count']}")
        print(f"    - 有README: {data['structure']['has_readme']}")


async def test_github_sync():
    """测试GitHub同步"""
    print("\n🔄 测试GitHub同步...")
    
    sync = GitHubSync()
    
    # 测试项目状态保存
    print("  分析项目状态...")
    analyzer = ProjectAnalyzer()
    project_statuses = await analyzer.analyze_all_projects()
    
    print("  保存项目状态到数据库...")
    async with sync.db.get_db() as conn:
        await sync.save_project_statuses(project_statuses, conn)
    
    print("  项目状态保存完成")


async def main():
    """主测试函数"""
    print("🚀 开始测试项目状态功能...")
    
    # 初始化数据库
    print("📊 初始化数据库...")
    await init_db()
    
    # 测试项目分析器
    await test_project_analyzer()
    
    # 测试GitHub同步
    await test_github_sync()
    
    print("\n✅ 测试完成！")


if __name__ == "__main__":
    asyncio.run(main()) 