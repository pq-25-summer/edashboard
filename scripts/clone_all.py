#!/usr/bin/env python3
"""
克隆所有学员项目脚本

从projects.txt读取项目列表，克隆所有项目到指定目录。
支持owner/repo的目录结构以避免同名冲突。
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path
from typing import List, Tuple, Optional
from urllib.parse import urlparse
import logging


class ProjectCloner:
    def __init__(self, target_dir: str, projects_file: str = "projects.txt"):
        self.target_dir = Path(target_dir)
        self.projects_file = Path(projects_file)
        self.setup_logging()
        
    def setup_logging(self):
        """设置日志"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler('clone_all.log')
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def read_projects(self) -> List[Tuple[str, str]]:
        """读取项目列表文件"""
        projects = []
        
        if not self.projects_file.exists():
            self.logger.error(f"项目文件不存在: {self.projects_file}")
            return projects
        
        try:
            with open(self.projects_file, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    
                    # 解析项目名称和GitHub URL
                    parts = line.split('\t')
                    if len(parts) != 2:
                        self.logger.warning(f"第{line_num}行格式错误: {line}")
                        continue
                    
                    project_name, github_url = parts
                    projects.append((project_name.strip(), github_url.strip()))
            
            self.logger.info(f"成功读取 {len(projects)} 个项目")
            return projects
            
        except Exception as e:
            self.logger.error(f"读取项目文件失败: {e}")
            return projects
    
    def extract_owner_repo(self, github_url: str) -> Optional[Tuple[str, str]]:
        """从GitHub URL提取owner和repo名称"""
        try:
            parsed = urlparse(github_url)
            if parsed.netloc != 'github.com':
                return None
            
            path_parts = parsed.path.strip('/').split('/')
            if len(path_parts) < 2:
                return None
            
            owner = path_parts[0]
            repo = path_parts[1].replace('.git', '')
            return owner, repo
            
        except Exception as e:
            self.logger.error(f"解析GitHub URL失败 {github_url}: {e}")
            return None
    
    def get_clone_path(self, owner: str, repo: str) -> Path:
        """获取克隆目标路径"""
        return self.target_dir / owner / repo
    
    def clone_repository(self, github_url: str, target_path: Path) -> bool:
        """克隆单个仓库"""
        try:
            # 确保目标目录存在
            target_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 如果目录已存在，跳过
            if target_path.exists():
                self.logger.info(f"目录已存在，跳过: {target_path}")
                return True
            
            # 执行git clone
            self.logger.info(f"克隆仓库: {github_url} -> {target_path}")
            result = subprocess.run(
                ['git', 'clone', github_url, str(target_path)],
                capture_output=True,
                text=True,
                timeout=300  # 5分钟超时
            )
            
            if result.returncode == 0:
                self.logger.info(f"成功克隆: {target_path}")
                return True
            else:
                self.logger.error(f"克隆失败 {github_url}: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            self.logger.error(f"克隆超时: {github_url}")
            return False
        except Exception as e:
            self.logger.error(f"克隆异常 {github_url}: {e}")
            return False
    
    def clone_all_projects(self) -> Tuple[int, int]:
        """克隆所有项目"""
        projects = self.read_projects()
        if not projects:
            return 0, 0
        
        # 确保目标目录存在
        self.target_dir.mkdir(parents=True, exist_ok=True)
        
        success_count = 0
        total_count = len(projects)
        
        self.logger.info(f"开始克隆 {total_count} 个项目到: {self.target_dir}")
        
        for project_name, github_url in projects:
            # 提取owner和repo
            owner_repo = self.extract_owner_repo(github_url)
            if not owner_repo:
                self.logger.error(f"无法解析GitHub URL: {github_url}")
                continue
            
            owner, repo = owner_repo
            target_path = self.get_clone_path(owner, repo)
            
            if self.clone_repository(github_url, target_path):
                success_count += 1
        
        return success_count, total_count
    
    def print_summary(self, success_count: int, total_count: int):
        """打印克隆结果摘要"""
        self.logger.info("=" * 50)
        self.logger.info("克隆完成摘要:")
        self.logger.info(f"总项目数: {total_count}")
        self.logger.info(f"成功克隆: {success_count}")
        self.logger.info(f"失败数量: {total_count - success_count}")
        self.logger.info(f"成功率: {success_count/total_count*100:.1f}%" if total_count > 0 else "0%")
        self.logger.info(f"目标目录: {self.target_dir}")
        self.logger.info("=" * 50)


def main():
    parser = argparse.ArgumentParser(
        description="克隆所有学员项目到指定目录",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python clone_all.py /path/to/repos
  python clone_all.py /path/to/repos --projects-file custom_projects.txt
        """
    )
    
    parser.add_argument(
        'target_dir',
        help='克隆目标目录'
    )
    
    parser.add_argument(
        '--projects-file',
        default='projects.txt',
        help='项目列表文件路径 (默认: projects.txt)'
    )
    
    args = parser.parse_args()
    
    # 创建克隆器
    cloner = ProjectCloner(args.target_dir, args.projects_file)
    
    # 执行克隆
    success_count, total_count = cloner.clone_all_projects()
    
    # 打印摘要
    cloner.print_summary(success_count, total_count)
    
    # 返回适当的退出码
    if success_count == total_count:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == '__main__':
    main() 