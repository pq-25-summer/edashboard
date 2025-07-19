#!/usr/bin/env python3
"""
检查项目README文档脚本

检查所有项目的README文档情况，包括：
- 是否包含README文件
- README文件的类型（.md, .txt, 等）
- README文件的大小
"""

import os
import sys
import argparse
from pathlib import Path
from typing import List, Dict, Tuple
import logging
from datetime import datetime


class ReadmeChecker:
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
                logging.FileHandler('check_readme.log')
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
    
    def check_readme_files(self, repo_path: Path) -> Dict:
        """检查单个仓库的README文件"""
        readme_info = {
            'has_readme': False,
            'readme_files': [],
            'readme_count': 0,
            'total_size': 0
        }
        
        # 常见的README文件名
        readme_patterns = [
            'README.md', 'README.txt', 'README.rst', 'README',
            'readme.md', 'readme.txt', 'readme.rst', 'readme',
            'Readme.md', 'Readme.txt', 'Readme.rst', 'Readme'
        ]
        
        for pattern in readme_patterns:
            readme_path = repo_path / pattern
            if readme_path.exists() and readme_path.is_file():
                readme_info['has_readme'] = True
                file_info = {
                    'name': pattern,
                    'path': str(readme_path),
                    'size': readme_path.stat().st_size,
                    'size_kb': round(readme_path.stat().st_size / 1024, 2)
                }
                readme_info['readme_files'].append(file_info)
                readme_info['total_size'] += file_info['size']
                readme_info['readme_count'] += 1
        
        return readme_info
    
    def check_all_repos(self) -> Dict[str, Dict]:
        """检查所有仓库的README文件"""
        git_repos = self.find_git_repos()
        if not git_repos:
            return {}
        
        results = {}
        
        for repo_path in git_repos:
            # 获取相对路径作为项目标识
            relative_path = repo_path.relative_to(self.base_dir)
            project_key = str(relative_path).replace('/', '/')
            
            readme_info = self.check_readme_files(repo_path)
            results[project_key] = {
                'path': str(repo_path),
                'relative_path': str(relative_path),
                **readme_info
            }
        
        return results
    
    def generate_summary(self, results: Dict[str, Dict]) -> Dict:
        """生成统计摘要"""
        total_repos = len(results)
        repos_with_readme = sum(1 for info in results.values() if info['has_readme'])
        repos_without_readme = total_repos - repos_with_readme
        
        # 统计README文件类型
        readme_types = {}
        total_readme_files = 0
        
        for info in results.values():
            for readme_file in info['readme_files']:
                ext = Path(readme_file['name']).suffix.lower()
                readme_types[ext] = readme_types.get(ext, 0) + 1
                total_readme_files += 1
        
        return {
            'total_repos': total_repos,
            'repos_with_readme': repos_with_readme,
            'repos_without_readme': repos_without_readme,
            'readme_coverage': round(repos_with_readme / total_repos * 100, 1) if total_repos > 0 else 0,
            'total_readme_files': total_readme_files,
            'readme_types': readme_types
        }
    
    def print_results(self, results: Dict[str, Dict], summary: Dict):
        """打印检查结果"""
        self.logger.info("=" * 60)
        self.logger.info("README文档检查结果")
        self.logger.info("=" * 60)
        
        # 打印摘要
        self.logger.info(f"总项目数: {summary['total_repos']}")
        self.logger.info(f"包含README的项目: {summary['repos_with_readme']}")
        self.logger.info(f"不包含README的项目: {summary['repos_without_readme']}")
        self.logger.info(f"README覆盖率: {summary['readme_coverage']}%")
        self.logger.info(f"README文件总数: {summary['total_readme_files']}")
        
        if summary['readme_types']:
            self.logger.info("README文件类型分布:")
            for ext, count in summary['readme_types'].items():
                self.logger.info(f"  {ext or '(无扩展名)'}: {count} 个")
        
        self.logger.info("\n详细结果:")
        self.logger.info("-" * 60)
        
        # 按是否有README分组显示
        with_readme = []
        without_readme = []
        
        for project_key, info in results.items():
            if info['has_readme']:
                with_readme.append((project_key, info))
            else:
                without_readme.append((project_key, info))
        
        # 显示有README的项目
        if with_readme:
            self.logger.info(f"\n✅ 包含README的项目 ({len(with_readme)} 个):")
            for project_key, info in sorted(with_readme):
                readme_names = [f['name'] for f in info['readme_files']]
                self.logger.info(f"  {project_key}: {', '.join(readme_names)}")
        
        # 显示没有README的项目
        if without_readme:
            self.logger.info(f"\n❌ 不包含README的项目 ({len(without_readme)} 个):")
            for project_key, info in sorted(without_readme):
                self.logger.info(f"  {project_key}")
        
        self.logger.info("=" * 60)
    
    def generate_markdown_report(self, results: Dict[str, Dict], summary: Dict) -> str:
        """生成Markdown格式的报告"""
        report = []
        
        # 标题
        report.append("# README文档检查报告")
        report.append("")
        
        # 摘要
        report.append("## 📊 统计摘要")
        report.append("")
        report.append(f"- **总项目数**: {summary['total_repos']}")
        report.append(f"- **包含README的项目**: {summary['repos_with_readme']}")
        report.append(f"- **不包含README的项目**: {summary['repos_without_readme']}")
        report.append(f"- **README覆盖率**: {summary['readme_coverage']}%")
        report.append(f"- **README文件总数**: {summary['total_readme_files']}")
        report.append("")
        
        # README文件类型分布
        if summary['readme_types']:
            report.append("### README文件类型分布")
            report.append("")
            for ext, count in summary['readme_types'].items():
                ext_name = ext if ext else "(无扩展名)"
                report.append(f"- {ext_name}: {count} 个")
            report.append("")
        
        # 详细结果
        report.append("## 📋 详细结果")
        report.append("")
        
        # 按是否有README分组
        with_readme = []
        without_readme = []
        
        for project_key, info in results.items():
            if info['has_readme']:
                with_readme.append((project_key, info))
            else:
                without_readme.append((project_key, info))
        
        # 有README的项目
        if with_readme:
            report.append("### ✅ 包含README的项目")
            report.append("")
            for project_key, info in sorted(with_readme):
                readme_names = [f['name'] for f in info['readme_files']]
                report.append(f"- **{project_key}**: {', '.join(readme_names)}")
            report.append("")
        
        # 没有README的项目
        if without_readme:
            report.append("### ❌ 不包含README的项目")
            report.append("")
            for project_key, info in sorted(without_readme):
                report.append(f"- **{project_key}**")
            report.append("")
        
        # 建议
        report.append("## 💡 建议")
        report.append("")
        if without_readme:
            report.append("建议以下项目添加README文档:")
            report.append("")
            for project_key, info in sorted(without_readme):
                report.append(f"- {project_key}")
            report.append("")
            report.append("README文档应包含:")
            report.append("- 项目简介和功能说明")
            report.append("- 安装和使用方法")
            report.append("- 技术栈和依赖")
            report.append("- 贡献指南")
        else:
            report.append("🎉 所有项目都包含README文档！")
        
        return "\n".join(report)


def main():
    parser = argparse.ArgumentParser(
        description="检查项目README文档情况",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python check_readme.py /path/to/repos
  python check_readme.py /path/to/repos --output report.md
        """
    )
    
    parser.add_argument(
        'base_dir',
        help='包含Git仓库的基础目录'
    )
    
    parser.add_argument(
        '--output',
        help='输出Markdown报告到指定文件'
    )
    
    parser.add_argument(
        '--json',
        help='输出JSON格式的结果到指定文件'
    )
    
    args = parser.parse_args()
    
    # 创建检查器
    checker = ReadmeChecker(args.base_dir)
    
    # 检查所有仓库
    results = checker.check_all_repos()
    
    if not results:
        print("未找到任何Git仓库")
        sys.exit(1)
    
    # 生成摘要
    summary = checker.generate_summary(results)
    
    # 打印结果
    checker.print_results(results, summary)
    
    # 生成Markdown报告
    if args.output:
        markdown_report = checker.generate_markdown_report(results, summary)
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(markdown_report)
        print(f"\nMarkdown报告已保存到: {args.output}")
    
    # 生成JSON结果
    if args.json:
        import json
        json_data = {
            'summary': summary,
            'results': results,
            'timestamp': datetime.now().isoformat()
        }
        with open(args.json, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)
        print(f"\nJSON结果已保存到: {args.json}")
    
    # 返回适当的退出码
    if summary['repos_without_readme'] == 0:
        sys.exit(0)  # 所有项目都有README
    else:
        sys.exit(1)  # 有项目缺少README


if __name__ == '__main__':
    main() 