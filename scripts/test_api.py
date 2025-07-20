#!/usr/bin/env python3
"""
测试API功能
"""

import asyncio
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backend'))

from app.project_analyzer import ProjectAnalyzer
from app.language_analyzer import LanguageAnalyzer


async def test_project_analyzer():
    """测试项目分析器"""
    print("🔍 测试项目分析器...")
    
    try:
        analyzer = ProjectAnalyzer()
        projects = await analyzer.analyze_all_projects()
        
        print(f"✅ 成功分析 {len(projects)} 个项目")
        
        # 检查第一个项目的技术栈
        if projects:
            first_project = list(projects.keys())[0]
            project_data = projects[first_project]
            
            print(f"\n📁 第一个项目: {first_project}")
            print(f"  技术栈: {project_data.get('tech_stack', {}).get('summary', {})}")
            
            return True
        else:
            print("❌ 没有找到项目")
            return False
            
    except Exception as e:
        print(f"❌ 项目分析器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_language_analyzer():
    """测试语言分析器"""
    print("\n🔍 测试语言分析器...")
    
    try:
        analyzer = LanguageAnalyzer()
        
        # 测试当前项目
        current_project = Path("/Users/mars/jobs/pq/edashboard")
        tech_stack = analyzer.analyze_project_tech_stack(current_project)
        
        print(f"✅ 成功分析当前项目")
        print(f"  主要语言: {tech_stack['summary'].get('primary_language', 'Unknown')}")
        print(f"  框架数量: {tech_stack['summary'].get('framework_count', 0)}")
        print(f"  使用AI: {tech_stack['summary'].get('has_ai', False)}")
        
        return True
        
    except Exception as e:
        print(f"❌ 语言分析器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """主函数"""
    print("🚀 API功能测试")
    print("=" * 50)
    
    # 测试项目分析器
    project_test = await test_project_analyzer()
    
    # 测试语言分析器
    language_test = await test_language_analyzer()
    
    if project_test and language_test:
        print("\n✅ 所有测试通过!")
        print("\n现在可以启动后端服务:")
        print("cd backend && uvicorn main:app --reload")
    else:
        print("\n❌ 部分测试失败，请检查错误信息")


if __name__ == "__main__":
    asyncio.run(main()) 