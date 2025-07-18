#!/usr/bin/env python3
"""
环境变量设置脚本
帮助开发者快速配置开发环境
"""

import os
import sys
import base64
from pathlib import Path


def create_env_file():
    """创建.env文件"""
    env_file = Path("../backend/.env")
    
    if env_file.exists():
        print("⚠️  .env文件已存在，是否要覆盖？(y/N): ", end="")
        if input().lower() != 'y':
            print("❌ 操作已取消")
            return False
    
    # 获取GitHub token
    print("🔑 请输入GitHub Personal Access Token:")
    print("   如果没有token，请访问: https://github.com/settings/tokens")
    print("   需要权限: repo, read:user")
    github_token = input("   Token: ").strip()
    
    if not github_token:
        print("❌ GitHub token不能为空")
        return False
    
    # 创建.env文件内容
    env_content = f"""# 数据库配置
DATABASE_URL=postgresql://localhost/edashboard

# GitHub API配置
GITHUB_TOKEN={github_token}
GITHUB_API_BASE_URL=https://api.github.com

# 应用配置
APP_NAME=软件工程课看板系统
DEBUG=true

# 安全配置
SECRET_KEY=dev-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
"""
    
    # 写入文件
    try:
        env_file.write_text(env_content, encoding='utf-8')
        print(f"✅ .env文件已创建: {env_file}")
        return True
    except Exception as e:
        print(f"❌ 创建.env文件失败: {e}")
        return False


def create_k8s_secret():
    """创建Kubernetes secret配置"""
    print("\n🔑 请输入GitHub Personal Access Token (用于Kubernetes):")
    github_token = input("   Token: ").strip()
    
    if not github_token:
        print("❌ GitHub token不能为空")
        return False
    
    # 生成base64编码
    token_b64 = base64.b64encode(github_token.encode()).decode()
    
    # 创建secret文件内容
    secret_content = f"""apiVersion: v1
kind: Secret
metadata:
  name: github-secret
  namespace: edashboard
type: Opaque
data:
  token: {token_b64}
"""
    
    # 写入文件
    secret_file = Path("../k8s/github-secret.yaml")
    try:
        secret_file.write_text(secret_content, encoding='utf-8')
        print(f"✅ Kubernetes secret文件已创建: {secret_file}")
        print("⚠️  注意：此文件包含敏感信息，请确保不要提交到版本控制")
        return True
    except Exception as e:
        print(f"❌ 创建secret文件失败: {e}")
        return False


def main():
    """主函数"""
    print("🚀 环境变量设置工具")
    print("=" * 50)
    
    # 检查当前目录
    if not Path("../backend").exists():
        print("❌ 请在scripts目录下运行此脚本")
        sys.exit(1)
    
    print("请选择要配置的环境:")
    print("1. 开发环境 (.env文件)")
    print("2. Kubernetes环境 (secret文件)")
    print("3. 两者都配置")
    
    choice = input("\n请输入选择 (1/2/3): ").strip()
    
    success = True
    
    if choice in ['1', '3']:
        print("\n📝 配置开发环境...")
        success &= create_env_file()
    
    if choice in ['2', '3']:
        print("\n☸️  配置Kubernetes环境...")
        success &= create_k8s_secret()
    
    if success:
        print("\n🎉 环境配置完成！")
        print("\n📋 下一步:")
        if choice in ['1', '3']:
            print("   - 启动后端服务: cd ../backend && python -m uvicorn main:app --reload")
        if choice in ['2', '3']:
            print("   - 应用Kubernetes配置: kubectl apply -f ../k8s/")
    else:
        print("\n❌ 配置过程中出现错误，请检查输入")
        sys.exit(1)


if __name__ == "__main__":
    main() 