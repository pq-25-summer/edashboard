#!/usr/bin/env python3
"""
API测试脚本
测试测试分析相关的API端点
"""

import requests
import json
import time

def test_api():
    base_url = "http://localhost:8000/api"
    
    print("=" * 50)
    print("测试分析API测试")
    print("=" * 50)
    
    # 等待服务启动
    print("等待服务启动...")
    time.sleep(3)
    
    # 测试健康检查
    try:
        response = requests.get("http://localhost:8000/health")
        print(f"健康检查: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"健康检查失败: {e}")
        return
    
    # 测试获取摘要
    try:
        response = requests.get(f"{base_url}/test-analysis/summary")
        print(f"获取摘要: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("摘要数据:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
        else:
            print(f"错误响应: {response.text}")
    except Exception as e:
        print(f"获取摘要失败: {e}")
    
    # 测试获取项目列表
    try:
        response = requests.get(f"{base_url}/test-analysis/projects")
        print(f"\n获取项目列表: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"找到 {len(data)} 个项目")
            if data:
                print("前3个项目:")
                for i, project in enumerate(data[:3]):
                    print(f"  {i+1}. {project.get('project_name', 'Unknown')}")
        else:
            print(f"错误响应: {response.text}")
    except Exception as e:
        print(f"获取项目列表失败: {e}")
    
    # 测试分析所有项目
    try:
        print(f"\n开始分析所有项目...")
        response = requests.post(f"{base_url}/test-analysis/analyze-all")
        print(f"分析结果: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"分析完成: {data.get('message', 'Unknown')}")
        else:
            print(f"错误响应: {response.text}")
    except Exception as e:
        print(f"分析失败: {e}")

if __name__ == "__main__":
    test_api() 