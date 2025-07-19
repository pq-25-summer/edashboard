#!/usr/bin/env python3
"""
README检查完整工作流程

1. 克隆所有项目（如果还没有）
2. 检查所有项目的README文档
3. 将结果发布到GitHub Issue
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path
from typing import Optional


def run_command(cmd: list, cwd: Optional[str] = None) -> bool:
    """运行命令并返回是否成功"""
    try:
        print(f"🔄 执行命令: {' '.join(cmd)}")
        result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print("✅ 命令执行成功")
            if result.stdout.strip():
                print(f"输出: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ 命令执行失败: {result.stderr.strip()}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ 命令执行超时")
        return False
    except Exception as e:
        print(f"❌ 命令执行异常: {e}")
        return False


def check_git_repos_exist(base_dir: str) -> bool:
    """检查是否已经存在Git仓库"""
    base_path = Path(base_dir)
    if not base_path.exists():
        return False
    
    # 查找.git目录
    git_dirs = list(base_path.rglob('.git'))
    return len(git_dirs) > 0


def main():
    parser = argparse.ArgumentParser(
        description="README检查完整工作流程",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
完整工作流程:
1. 克隆所有项目到指定目录
2. 检查所有项目的README文档
3. 将结果发布到GitHub Issue

示例:
  python readme_workflow.py /path/to/repos --owner pq-25-summer --repo edashboard --issue 1
  python readme_workflow.py /path/to/repos --owner pq-25-summer --repo edashboard --issue 1 --skip-clone
        """
    )
    
    parser.add_argument(
        'base_dir',
        help='项目存储目录'
    )
    
    parser.add_argument(
        '--owner',
        required=True,
        help='GitHub仓库所有者'
    )
    
    parser.add_argument(
        '--repo',
        required=True,
        help='GitHub仓库名称'
    )
    
    parser.add_argument(
        '--issue',
        type=int,
        required=True,
        help='Issue编号'
    )
    
    parser.add_argument(
        '--projects-file',
        default='scripts/projects.txt',
        help='项目列表文件路径'
    )
    
    parser.add_argument(
        '--skip-clone',
        action='store_true',
        help='跳过克隆步骤（如果项目已经存在）'
    )
    
    parser.add_argument(
        '--token',
        help='GitHub Token (也可通过GITHUB_TOKEN环境变量设置)'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='预览模式，不实际发布评论'
    )
    
    args = parser.parse_args()
    
    print("🚀 开始README检查工作流程")
    print("=" * 50)
    
    # 步骤1: 克隆项目（如果需要）
    if not args.skip_clone:
        print("\n📥 步骤1: 克隆项目")
        print("-" * 30)
        
        if check_git_repos_exist(args.base_dir):
            print(f"⚠️  目录 {args.base_dir} 中已存在Git仓库")
            response = input("是否继续克隆？可能会跳过已存在的项目 (y/N): ")
            if response.lower() != 'y':
                print("❌ 用户取消操作")
                sys.exit(1)
        
        clone_cmd = [
            'python', 'scripts/clone_all.py',
            args.base_dir,
            '--projects-file', args.projects_file
        ]
        
        if not run_command(clone_cmd):
            print("❌ 克隆项目失败")
            sys.exit(1)
    else:
        print("\n⏭️  步骤1: 跳过克隆（用户指定）")
    
    # 步骤2: 检查README文档
    print("\n📋 步骤2: 检查README文档")
    print("-" * 30)
    
    # 生成临时文件名
    import tempfile
    temp_dir = tempfile.mkdtemp()
    json_file = os.path.join(temp_dir, 'readme_results.json')
    markdown_file = os.path.join(temp_dir, 'readme_report.md')
    
    check_cmd = [
        'python', 'scripts/check_readme.py',
        args.base_dir,
        '--json', json_file,
        '--output', markdown_file
    ]
    
    if not run_command(check_cmd):
        print("❌ 检查README文档失败")
        sys.exit(1)
    
    # 检查结果文件是否存在
    if not os.path.exists(json_file):
        print("❌ 未生成结果文件")
        sys.exit(1)
    
    # 步骤3: 发布到GitHub Issue
    print("\n📤 步骤3: 发布到GitHub Issue")
    print("-" * 30)
    
    post_cmd = [
        'python', 'scripts/post_readme_report.py',
        '--owner', args.owner,
        '--repo', args.repo,
        '--issue', str(args.issue),
        '--results', json_file
    ]
    
    if args.token:
        post_cmd.extend(['--token', args.token])
    
    if args.dry_run:
        post_cmd.append('--dry-run')
    
    if not run_command(post_cmd):
        print("❌ 发布到GitHub Issue失败")
        sys.exit(1)
    
    # 清理临时文件
    try:
        import shutil
        shutil.rmtree(temp_dir)
        print(f"\n🧹 已清理临时文件: {temp_dir}")
    except Exception as e:
        print(f"\n⚠️  清理临时文件失败: {e}")
    
    print("\n🎉 工作流程完成！")
    print("=" * 50)


if __name__ == '__main__':
    main() 