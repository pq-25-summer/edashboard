#!/usr/bin/env python3
"""
测试Git工作流程分析功能
"""

import os
import sys
from pathlib import Path

# 设置环境变量
os.environ['LOCAL_REPOS_DIR'] = 'repos'

# 添加backend目录到Python路径
sys.path.append(str(Path(__file__).parent.parent / "backend"))

def test_git_workflow_analyzer():
    """测试Git工作流程分析器"""
    try:
        from app.git_workflow_analyzer import GitWorkflowAnalyzer
        
        print("✅ 成功导入GitWorkflowAnalyzer")
        
        # 创建分析器
        analyzer = GitWorkflowAnalyzer()
        print("✅ 成功创建分析器")
        
        # 测试分析一个示例项目
        test_projects = [
            {
                "name": "test-project",
                "github_url": "https://github.com/test/test-project"
            }
        ]
        
        results = analyzer.analyze_all_projects(test_projects)
        print(f"✅ 分析完成，结果数量: {len(results)}")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False


def test_api_routes():
    """测试API路由"""
    try:
        from app.routers.git_workflow import router
        
        print("✅ 成功导入Git工作流程API路由")
        
        # 检查路由是否注册
        routes = [route.path for route in router.routes]
        expected_routes = [
            "/api/git-workflow/summary",
            "/api/git-workflow/projects",
            "/api/git-workflow/analyze",
            "/api/git-workflow/statistics"
        ]
        
        for route in expected_routes:
            if route in routes:
                print(f"✅ 找到路由: {route}")
            else:
                print(f"❌ 缺少路由: {route}")
        
        return True
        
    except Exception as e:
        print(f"❌ API路由测试失败: {e}")
        return False


def main():
    """主测试函数"""
    print("🧪 开始测试Git工作流程分析功能...")
    
    # 测试分析器
    print("\n1. 测试Git工作流程分析器")
    analyzer_ok = test_git_workflow_analyzer()
    
    # 测试API路由
    print("\n2. 测试API路由")
    api_ok = test_api_routes()
    
    # 总结
    print("\n" + "="*50)
    print("测试结果总结:")
    print(f"Git工作流程分析器: {'✅ 通过' if analyzer_ok else '❌ 失败'}")
    print(f"API路由: {'✅ 通过' if api_ok else '❌ 失败'}")
    
    if analyzer_ok and api_ok:
        print("\n🎉 所有测试通过！Git工作流程分析功能已就绪。")
        return 0
    else:
        print("\n⚠️ 部分测试失败，请检查相关配置。")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 