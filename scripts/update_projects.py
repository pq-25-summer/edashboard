#!/usr/bin/env python3
"""
项目更新脚本

在包含.git目录的项目子目录中执行git pull来更新项目。
支持批量更新和选择性更新。
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path
from typing import List, Tuple, Optional
import logging


class ProjectUpdater:
    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir)
        self.setup_logging()
        
    def setup_logging(self):
        """设置日志"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler('update_projects.log')
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def find_git_repos(self) -> List[Path]:
        """查找所有包含.git目录的项目目录"""
        git_repos = []
        
        if not self.base_dir.exists():
            self.logger.error(f"基础目录不存在: {self.base_dir}")
            return git_repos
        
        try:
            # 递归查找所有.git目录
            for git_dir in self.base_dir.rglob('.git'):
                if git_dir.is_dir():
                    # .git的父目录就是项目根目录
                    project_dir = git_dir.parent
                    git_repos.append(project_dir)
                    self.logger.debug(f"找到Git仓库: {project_dir}")
            
            self.logger.info(f"找到 {len(git_repos)} 个Git仓库")
            return git_repos
            
        except Exception as e:
            self.logger.error(f"查找Git仓库失败: {e}")
            return git_repos
    
    def get_git_status(self, repo_path: Path) -> str:
        """获取Git仓库状态"""
        try:
            result = subprocess.run(
                ['git', 'status', '--porcelain'],
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                return f"ERROR: {result.stderr.strip()}"
                
        except Exception as e:
            return f"ERROR: {str(e)}"
    
    def get_git_branch(self, repo_path: Path) -> str:
        """获取当前分支名"""
        try:
            result = subprocess.run(
                ['git', 'branch', '--show-current'],
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                return "unknown"
                
        except Exception as e:
            return "unknown"
    
    def update_repository(self, repo_path: Path, force: bool = False) -> bool:
        """更新单个仓库"""
        try:
            # 检查是否有未提交的更改
            git_status = self.get_git_status(repo_path)
            if git_status and not force:
                self.logger.warning(f"仓库有未提交的更改，跳过: {repo_path}")
                self.logger.warning(f"状态: {git_status}")
                return False
            
            # 获取当前分支
            current_branch = self.get_git_branch(repo_path)
            
            # 执行git pull
            self.logger.info(f"更新仓库: {repo_path} (分支: {current_branch})")
            result = subprocess.run(
                ['git', 'pull'],
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=300  # 5分钟超时
            )
            
            if result.returncode == 0:
                self.logger.info(f"成功更新: {repo_path}")
                if result.stdout.strip():
                    self.logger.info(f"更新内容: {result.stdout.strip()}")
                return True
            else:
                self.logger.error(f"更新失败 {repo_path}: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            self.logger.error(f"更新超时: {repo_path}")
            return False
        except Exception as e:
            self.logger.error(f"更新异常 {repo_path}: {e}")
            return False
    
    def update_all_repos(self, force: bool = False) -> Tuple[int, int]:
        """更新所有仓库"""
        git_repos = self.find_git_repos()
        if not git_repos:
            return 0, 0
        
        success_count = 0
        total_count = len(git_repos)
        
        self.logger.info(f"开始更新 {total_count} 个仓库")
        
        for repo_path in git_repos:
            if self.update_repository(repo_path, force):
                success_count += 1
        
        return success_count, total_count
    
    def update_specific_repo(self, repo_path: str, force: bool = False) -> bool:
        """更新指定的仓库"""
        repo_path = Path(repo_path)
        
        if not repo_path.exists():
            self.logger.error(f"仓库路径不存在: {repo_path}")
            return False
        
        if not (repo_path / '.git').exists():
            self.logger.error(f"不是Git仓库: {repo_path}")
            return False
        
        return self.update_repository(repo_path, force)
    
    def list_repos(self) -> None:
        """列出所有找到的Git仓库"""
        git_repos = self.find_git_repos()
        
        if not git_repos:
            self.logger.info("未找到任何Git仓库")
            return
        
        self.logger.info(f"找到 {len(git_repos)} 个Git仓库:")
        for i, repo_path in enumerate(git_repos, 1):
            relative_path = repo_path.relative_to(self.base_dir)
            current_branch = self.get_git_branch(repo_path)
            git_status = self.get_git_status(repo_path)
            
            status_text = "clean" if not git_status else "dirty"
            self.logger.info(f"{i:2d}. {relative_path} (分支: {current_branch}, 状态: {status_text})")
    
    def print_summary(self, success_count: int, total_count: int):
        """打印更新结果摘要"""
        self.logger.info("=" * 50)
        self.logger.info("更新完成摘要:")
        self.logger.info(f"总仓库数: {total_count}")
        self.logger.info(f"成功更新: {success_count}")
        self.logger.info(f"失败数量: {total_count - success_count}")
        self.logger.info(f"成功率: {success_count/total_count*100:.1f}%" if total_count > 0 else "0%")
        self.logger.info(f"基础目录: {self.base_dir}")
        self.logger.info("=" * 50)


def main():
    parser = argparse.ArgumentParser(
        description="更新Git仓库项目",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python update_projects.py /path/to/repos
  python update_projects.py /path/to/repos --force
  python update_projects.py /path/to/repos --list
  python update_projects.py /path/to/repos --repo /path/to/specific/repo
        """
    )
    
    parser.add_argument(
        'base_dir',
        help='包含Git仓库的基础目录'
    )
    
    parser.add_argument(
        '--force',
        action='store_true',
        help='强制更新，即使有未提交的更改'
    )
    
    parser.add_argument(
        '--list',
        action='store_true',
        help='列出所有找到的Git仓库'
    )
    
    parser.add_argument(
        '--repo',
        help='更新指定的单个仓库路径'
    )
    
    args = parser.parse_args()
    
    # 创建更新器
    updater = ProjectUpdater(args.base_dir)
    
    if args.list:
        # 列出所有仓库
        updater.list_repos()
        return
    
    if args.repo:
        # 更新指定仓库
        success = updater.update_specific_repo(args.repo, args.force)
        sys.exit(0 if success else 1)
    
    # 更新所有仓库
    success_count, total_count = updater.update_all_repos(args.force)
    
    # 打印摘要
    updater.print_summary(success_count, total_count)
    
    # 返回适当的退出码
    if success_count == total_count:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == '__main__':
    main() 