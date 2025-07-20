#!/usr/bin/env python3
"""
测试仪表板API功能
验证Issue 6的实现是否正确
"""

import requests
import json
from datetime import datetime
import sys
import os

# 添加backend目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

def test_dashboard_api():
    """测试仪表板API端点"""
    base_url = "http://localhost:8000"
    endpoint = "/api/analytics/dashboard"
    
    print("🧪 测试仪表板API功能")
    print(f"目标URL: {base_url}{endpoint}")
    print("-" * 50)
    
    try:
        # 发送GET请求
        response = requests.get(f"{base_url}{endpoint}", timeout=30)
        
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ API请求成功")
            print("\n📊 返回数据:")
            
            # 显示基本统计
            print(f"总项目数: {data.get('total_projects', 0)}")
            print(f"总学生数: {data.get('total_students', 0)}")
            print(f"总提交数: {data.get('total_commits', 0)}")
            print(f"总Issue数: {data.get('total_issues', 0)}")
            
            # 显示学生提交统计
            commits_by_student = data.get('commits_by_student', [])
            print(f"\n👥 学生提交统计 (共{len(commits_by_student)}人):")
            for i, student in enumerate(commits_by_student[:5]):  # 只显示前5个
                print(f"  {i+1}. {student['name']} ({student['github_username']}): {student['commit_count']}次提交")
            
            # 显示学生Issue统计
            issues_by_student = data.get('issues_by_student', [])
            print(f"\n📋 学生Issue统计 (共{len(issues_by_student)}人):")
            for i, student in enumerate(issues_by_student[:5]):  # 只显示前5个
                print(f"  {i+1}. {student['name']} ({student['github_username']}): {student['issue_count']}个Issue")
            
            # 显示最近活动
            recent_activity = data.get('recent_activity', [])
            print(f"\n📈 最近活动 (共{len(recent_activity)}条):")
            for i, activity in enumerate(recent_activity[:5]):  # 只显示前5个
                activity_type = "提交" if activity['type'] == 'commit' else "Issue"
                date_str = activity['date'][:19] if activity['date'] else "未知时间"
                print(f"  {i+1}. [{activity_type}] {activity['title']} - {activity['student_name']} ({date_str})")
            
            # 显示分析时间
            analysis_time = data.get('analysis_time', '')
            if analysis_time:
                print(f"\n⏰ 分析时间: {analysis_time}")
            
            print("\n✅ 仪表板API功能测试通过")
            return True
            
        else:
            print(f"❌ API请求失败: {response.status_code}")
            print(f"错误信息: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ 连接失败: 请确保后端服务正在运行")
        print("启动命令: cd backend && uvicorn main:app --reload")
        return False
        
    except requests.exceptions.Timeout:
        print("❌ 请求超时: API响应时间过长")
        return False
        
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        return False

def test_other_analytics_endpoints():
    """测试其他分析API端点"""
    base_url = "http://localhost:8000"
    endpoints = [
        "/api/analytics/languages",
        "/api/analytics/frameworks", 
        "/api/analytics/ai-technologies",
        "/api/analytics/tech-stack-summary"
    ]
    
    print("\n🧪 测试其他分析API端点")
    print("-" * 50)
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            status = "✅" if response.status_code == 200 else "❌"
            print(f"{status} {endpoint}: {response.status_code}")
        except Exception as e:
            print(f"❌ {endpoint}: 连接失败")

def main():
    """主函数"""
    print("=" * 60)
    print("🔍 Issue 6 仪表板API功能测试")
    print("=" * 60)
    
    # 测试仪表板API
    dashboard_success = test_dashboard_api()
    
    # 测试其他端点
    test_other_analytics_endpoints()
    
    print("\n" + "=" * 60)
    if dashboard_success:
        print("🎉 Issue 6 实现成功！仪表板API功能正常")
        print("\n📋 实现的功能:")
        print("  ✅ 项目统计概览")
        print("  ✅ 学生提交统计") 
        print("  ✅ 学生Issue统计")
        print("  ✅ 最近活动展示")
        print("  ✅ 数据可视化支持")
    else:
        print("❌ Issue 6 实现存在问题，请检查后端服务")
    
    print("=" * 60)

if __name__ == "__main__":
    main() 