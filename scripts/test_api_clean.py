#!/usr/bin/env python3
"""
测试API服务是否已清理分析逻辑
验证Issue 6的完整实现
"""

import requests
import time
import sys
from pathlib import Path

def test_api_endpoints():
    """测试API端点是否不再执行分析逻辑"""
    print("🧪 测试API端点是否已清理分析逻辑")
    print("-" * 50)
    
    base_url = "http://localhost:8000"
    
    # 测试端点列表
    endpoints = [
        "/api/analytics/dashboard",
        "/api/analytics/languages", 
        "/api/analytics/frameworks",
        "/api/analytics/ai-technologies",
        "/api/analytics/tech-stack-summary",
        "/api/project-status/",
        "/api/project-status/summary/overview"
    ]
    
    results = []
    
    for endpoint in endpoints:
        try:
            print(f"测试端点: {endpoint}")
            start_time = time.time()
            
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            
            end_time = time.time()
            response_time = end_time - start_time
            
            print(f"  响应时间: {response_time:.2f}秒")
            print(f"  状态码: {response.status_code}")
            
            # 检查响应时间，如果超过2秒可能还在执行分析
            if response_time > 2.0:
                print(f"  ⚠️  响应时间较长，可能仍在执行分析")
                results.append((endpoint, False, f"响应时间过长: {response_time:.2f}秒"))
            else:
                print(f"  ✅ 响应时间正常")
                results.append((endpoint, True, f"响应时间: {response_time:.2f}秒"))
                
        except requests.exceptions.RequestException as e:
            print(f"  ❌ 请求失败: {e}")
            results.append((endpoint, False, f"请求失败: {e}"))
        except Exception as e:
            print(f"  ❌ 测试异常: {e}")
            results.append((endpoint, False, f"测试异常: {e}"))
        
        print()
    
    return results

def test_removed_endpoints():
    """测试已移除的分析端点"""
    print("🧪 测试已移除的分析端点")
    print("-" * 50)
    
    base_url = "http://localhost:8000"
    
    # 应该被移除的端点
    removed_endpoints = [
        ("/api/project-status/analyze", "POST"),
        ("/api/project-status/update-repos", "POST"),
        ("/api/project-status/sync", "POST"),
        ("/api/project-status/analysis-only", "POST"),
        ("/api/project-status/scheduler/status", "GET")
    ]
    
    results = []
    
    for endpoint, method in removed_endpoints:
        try:
            print(f"测试已移除端点: {method} {endpoint}")
            
            if method == "GET":
                response = requests.get(f"{base_url}{endpoint}", timeout=5)
            else:
                response = requests.post(f"{base_url}{endpoint}", timeout=5)
            
            print(f"  状态码: {response.status_code}")
            
            # 应该返回400错误，提示使用独立脚本
            if response.status_code == 400:
                print(f"  ✅ 正确返回400错误")
                print(f"  错误信息: {response.json().get('detail', '')}")
                results.append((endpoint, True, "正确返回400错误"))
            else:
                print(f"  ❌ 未正确返回400错误")
                results.append((endpoint, False, f"状态码: {response.status_code}"))
                
        except requests.exceptions.RequestException as e:
            print(f"  ❌ 请求失败: {e}")
            results.append((endpoint, False, f"请求失败: {e}"))
        except Exception as e:
            print(f"  ❌ 测试异常: {e}")
            results.append((endpoint, False, f"测试异常: {e}"))
        
        print()
    
    return results

def main():
    """主测试函数"""
    print("=" * 60)
    print("🔍 API服务清理测试")
    print("=" * 60)
    
    print("请确保后端服务正在运行: uvicorn main:app --reload")
    print("按Enter键继续...")
    input()
    
    # 测试API端点
    api_results = test_api_endpoints()
    
    print("\n" + "=" * 60)
    
    # 测试已移除的端点
    removed_results = test_removed_endpoints()
    
    print("\n" + "=" * 60)
    print("📊 测试结果汇总")
    print("=" * 60)
    
    all_results = api_results + removed_results
    
    passed = 0
    total = len(all_results)
    
    print("\nAPI端点响应时间测试:")
    for endpoint, success, message in api_results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"  {endpoint}: {status} - {message}")
        if success:
            passed += 1
    
    print("\n已移除端点测试:")
    for endpoint, success, message in removed_results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"  {endpoint}: {status} - {message}")
        if success:
            passed += 1
    
    print(f"\n总计: {passed}/{total} 项测试通过")
    
    if passed == total:
        print("\n🎉 API服务清理测试全部通过!")
        print("\n📋 验证的功能:")
        print("  ✅ API端点不再执行实时分析")
        print("  ✅ 响应时间大幅缩短")
        print("  ✅ 分析端点已正确移除")
        print("  ✅ 提示用户使用独立脚本")
        return True
    else:
        print(f"\n❌ 有 {total - passed} 项测试失败")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 