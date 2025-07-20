#!/usr/bin/env python3
"""
Issue 6 实现测试脚本
验证分离后台任务的实现

测试内容:
1. 验证定时任务已从主应用中移除
2. 测试独立脚本功能
3. 验证Kubernetes配置文件
"""

import os
import sys
import subprocess
import importlib.util
from pathlib import Path

def test_scheduler_removal():
    """测试定时任务调度器是否已从主应用中移除"""
    print("🧪 测试定时任务调度器移除")
    print("-" * 40)
    
    main_py_path = Path("../backend/main.py")
    if not main_py_path.exists():
        print("❌ backend/main.py 文件不存在")
        return False
    
    with open(main_py_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查是否移除了调度器导入
    if "start_background_scheduler" in content:
        print("❌ 主应用中仍包含 start_background_scheduler")
        return False
    
    if "stop_background_scheduler" in content:
        print("❌ 主应用中仍包含 stop_background_scheduler")
        return False
    
    if "scheduler_task = asyncio.create_task" in content:
        print("❌ 主应用中仍包含调度器任务创建")
        return False
    
    print("✅ 定时任务调度器已从主应用中移除")
    return True

def test_standalone_scripts():
    """测试独立脚本是否存在"""
    print("\n🧪 测试独立脚本")
    print("-" * 40)
    
    scripts = [
        "sync_data.py",
        "analyze_projects.py", 
        "update_repos.py",
        "cli.py"
    ]
    
    all_exist = True
    for script in scripts:
        script_path = Path(script)
        if script_path.exists():
            print(f"✅ {script} 存在")
        else:
            print(f"❌ {script} 不存在")
            all_exist = False
    
    return all_exist

def test_script_executability():
    """测试脚本的可执行性"""
    print("\n🧪 测试脚本可执行性")
    print("-" * 40)
    
    # 测试CLI帮助信息
    try:
        result = subprocess.run(
            [sys.executable, "cli.py", "--help"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print("✅ CLI脚本可执行")
            print("📋 CLI帮助信息:")
            print(result.stdout)
            return True
        else:
            print(f"❌ CLI脚本执行失败: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ CLI脚本执行超时")
        return False
    except Exception as e:
        print(f"❌ CLI脚本执行异常: {e}")
        return False

def test_k8s_config():
    """测试Kubernetes配置文件"""
    print("\n🧪 测试Kubernetes配置文件")
    print("-" * 40)
    
    k8s_path = Path("../k8s/dev-environment.yaml")
    if not k8s_path.exists():
        print("❌ k8s/dev-environment.yaml 文件不存在")
        return False
    
    with open(k8s_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查必要的组件
    required_components = [
        "Namespace",
        "ConfigMap", 
        "Secret",
        "PersistentVolumeClaim",
        "Deployment",
        "Service",
        "CronJob"
    ]
    
    all_components = True
    for component in required_components:
        if component in content:
            print(f"✅ 包含 {component}")
        else:
            print(f"❌ 缺少 {component}")
            all_components = False
    
    return all_components

def test_script_content():
    """测试脚本内容是否正确"""
    print("\n🧪 测试脚本内容")
    print("-" * 40)
    
    # 测试sync_data.py
    sync_script = Path("sync_data.py")
    if sync_script.exists():
        with open(sync_script, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if "GitHubSync" in content and "sync_all_projects" in content:
            print("✅ sync_data.py 内容正确")
        else:
            print("❌ sync_data.py 内容不正确")
            return False
    
    # 测试analyze_projects.py
    analyze_script = Path("analyze_projects.py")
    if analyze_script.exists():
        with open(analyze_script, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if "ProjectAnalyzer" in content and "analyze_all_projects" in content:
            print("✅ analyze_projects.py 内容正确")
        else:
            print("❌ analyze_projects.py 内容不正确")
            return False
    
    # 测试update_repos.py
    update_script = Path("update_repos.py")
    if update_script.exists():
        with open(update_script, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if "ProjectAnalyzer" in content and "update_local_repos" in content:
            print("✅ update_repos.py 内容正确")
        else:
            print("❌ update_repos.py 内容不正确")
            return False
    
    return True

def main():
    """主测试函数"""
    print("=" * 60)
    print("🔍 Issue 6 实现测试")
    print("=" * 60)
    
    tests = [
        ("定时任务移除", test_scheduler_removal),
        ("独立脚本存在", test_standalone_scripts),
        ("脚本可执行性", test_script_executability),
        ("K8s配置文件", test_k8s_config),
        ("脚本内容", test_script_content)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} 测试异常: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 60)
    print("📊 测试结果汇总")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n总计: {passed}/{total} 项测试通过")
    
    if passed == total:
        print("\n🎉 Issue 6 实现测试全部通过!")
        print("\n📋 实现的功能:")
        print("  ✅ 移除定时任务调度器")
        print("  ✅ 创建独立命令行脚本")
        print("  ✅ 提供Kubernetes编排")
        print("  ✅ 支持独立任务执行")
        return True
    else:
        print(f"\n❌ 有 {total - passed} 项测试失败，请检查实现")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 