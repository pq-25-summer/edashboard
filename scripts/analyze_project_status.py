#!/usr/bin/env python3
"""
项目状态分析脚本

分析每个项目的详细状态，包括：
- README文档情况
- 项目结构
- 代码文件统计
- 文档文件统计
- 开发活跃度
"""

import os
import sys
import argparse
import json
from pathlib import Path
from typing import Dict, List, Tuple
import logging
from datetime import datetime
import subprocess


class ProjectAnalyzer:
    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir)
        self.setup_logging()
        
    def setup_logging(self):
        """设置日志"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def find_git_repos(self) -> List[Path]:
        """查找所有Git仓库"""
        git_repos = []
        
        if not self.base_dir.exists():
            self.logger.error(f"基础目录不存在: {self.base_dir}")
            return git_repos
        
        try:
            for git_dir in self.base_dir.rglob('.git'):
                if git_dir.is_dir():
                    project_dir = git_dir.parent
                    git_repos.append(project_dir)
            
            self.logger.info(f"找到 {len(git_repos)} 个Git仓库")
            return git_repos
            
        except Exception as e:
            self.logger.error(f"查找Git仓库失败: {e}")
            return git_repos
    
    def analyze_project_structure(self, repo_path: Path) -> Dict:
        """分析项目结构"""
        analysis = {
            'total_files': 0,
            'code_files': 0,
            'doc_files': 0,
            'config_files': 0,
            'other_files': 0,
            'directories': 0,
            'file_types': {},
            'has_package_json': False,
            'has_requirements_txt': False,
            'has_dockerfile': False,
            'has_readme': False,
            'readme_files': [],
            'main_language': None,
            'project_size_kb': 0
        }
        
        # 代码文件扩展名
        code_extensions = {
            '.py', '.js', '.ts', '.jsx', '.tsx', '.vue', '.java', '.cpp', '.c', 
            '.h', '.cs', '.php', '.rb', '.go', '.rs', '.swift', '.kt', '.scala',
            '.html', '.css', '.scss', '.sass', '.less', '.xml', '.json', '.yaml',
            '.yml', '.toml', '.ini', '.cfg', '.conf'
        }
        
        # 文档文件扩展名
        doc_extensions = {
            '.md', '.txt', '.rst', '.doc', '.docx', '.pdf', '.tex', '.adoc'
        }
        
        # 配置文件扩展名
        config_extensions = {
            '.json', '.yaml', '.yml', '.toml', '.ini', '.cfg', '.conf', '.env',
            '.gitignore', '.dockerignore', '.editorconfig'
        }
        
        total_size = 0
        
        try:
            for item in repo_path.rglob('*'):
                if item.is_file():
                    analysis['total_files'] += 1
                    file_size = item.stat().st_size
                    total_size += file_size
                    
                    # 跳过.git目录
                    if '.git' in str(item):
                        continue
                    
                    ext = item.suffix.lower()
                    analysis['file_types'][ext] = analysis['file_types'].get(ext, 0) + 1
                    
                    # 检查特殊文件
                    if item.name == 'package.json':
                        analysis['has_package_json'] = True
                    elif item.name == 'requirements.txt':
                        analysis['has_requirements_txt'] = True
                    elif item.name.lower() in ['dockerfile', 'docker-compose.yml', 'docker-compose.yaml']:
                        analysis['has_dockerfile'] = True
                    elif item.name.lower().startswith('readme'):
                        analysis['has_readme'] = True
                        analysis['readme_files'].append(item.name)
                    
                    # 分类文件
                    if ext in code_extensions:
                        analysis['code_files'] += 1
                    elif ext in doc_extensions:
                        analysis['doc_files'] += 1
                    elif ext in config_extensions:
                        analysis['config_files'] += 1
                    else:
                        analysis['other_files'] += 1
                        
                elif item.is_dir() and '.git' not in str(item):
                    analysis['directories'] += 1
            
            analysis['project_size_kb'] = round(total_size / 1024, 2)
            
            # 确定主要编程语言
            lang_counts = {}
            for ext, count in analysis['file_types'].items():
                if ext in ['.py']:
                    lang_counts['Python'] = lang_counts.get('Python', 0) + count
                elif ext in ['.js', '.jsx']:
                    lang_counts['JavaScript'] = lang_counts.get('JavaScript', 0) + count
                elif ext in ['.ts', '.tsx']:
                    lang_counts['TypeScript'] = lang_counts.get('TypeScript', 0) + count
                elif ext in ['.java']:
                    lang_counts['Java'] = lang_counts.get('Java', 0) + count
                elif ext in ['.cpp', '.c', '.h']:
                    lang_counts['C/C++'] = lang_counts.get('C/C++', 0) + count
                elif ext in ['.html', '.css']:
                    lang_counts['Web'] = lang_counts.get('Web', 0) + count
            
            if lang_counts:
                analysis['main_language'] = max(lang_counts, key=lang_counts.get)
            
        except Exception as e:
            self.logger.error(f"分析项目结构失败 {repo_path}: {e}")
        
        return analysis
    
    def get_git_info(self, repo_path: Path) -> Dict:
        """获取Git信息"""
        git_info = {
            'branch': 'unknown',
            'last_commit': 'unknown',
            'commit_count': 0,
            'contributors': 0
        }
        
        try:
            # 获取当前分支
            result = subprocess.run(
                ['git', 'branch', '--show-current'],
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                git_info['branch'] = result.stdout.strip()
            
            # 获取最后提交信息
            result = subprocess.run(
                ['git', 'log', '-1', '--format=%H|%an|%ad|%s', '--date=short'],
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0 and result.stdout.strip():
                parts = result.stdout.strip().split('|')
                if len(parts) >= 4:
                    git_info['last_commit'] = f"{parts[1]} ({parts[2]}): {parts[3]}"
            
            # 获取提交数量
            result = subprocess.run(
                ['git', 'rev-list', '--count', 'HEAD'],
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                git_info['commit_count'] = int(result.stdout.strip())
            
            # 获取贡献者数量
            result = subprocess.run(
                ['git', 'shortlog', '-sn', '--no-merges'],
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                git_info['contributors'] = len(result.stdout.strip().split('\n')) if result.stdout.strip() else 0
                
        except Exception as e:
            self.logger.error(f"获取Git信息失败 {repo_path}: {e}")
        
        return git_info
    
    def analyze_all_projects(self) -> Dict[str, Dict]:
        """分析所有项目"""
        git_repos = self.find_git_repos()
        if not git_repos:
            return {}
        
        results = {}
        
        for repo_path in git_repos:
            relative_path = repo_path.relative_to(self.base_dir)
            project_key = str(relative_path)
            
            self.logger.info(f"分析项目: {project_key}")
            
            # 分析项目结构
            structure = self.analyze_project_structure(repo_path)
            
            # 获取Git信息
            git_info = self.get_git_info(repo_path)
            
            results[project_key] = {
                'path': str(repo_path),
                'relative_path': str(relative_path),
                'structure': structure,
                'git_info': git_info,
                'analysis_time': datetime.now().isoformat()
            }
        
        return results
    
    def generate_project_report(self, project_key: str, project_data: Dict) -> str:
        """生成单个项目的报告"""
        structure = project_data['structure']
        git_info = project_data['git_info']
        
        report = []
        report.append(f"# 📊 项目状态报告: {project_key}")
        report.append("")
        
        # 基本信息
        report.append("## 📋 基本信息")
        report.append("")
        report.append(f"- **项目路径**: {project_data['relative_path']}")
        report.append(f"- **项目大小**: {structure['project_size_kb']} KB")
        report.append(f"- **主要语言**: {structure['main_language'] or '未知'}")
        report.append(f"- **当前分支**: {git_info['branch']}")
        report.append("")
        
        # 文件统计
        report.append("## 📁 文件统计")
        report.append("")
        report.append(f"- **总文件数**: {structure['total_files']}")
        report.append(f"- **代码文件**: {structure['code_files']}")
        report.append(f"- **文档文件**: {structure['doc_files']}")
        report.append(f"- **配置文件**: {structure['config_files']}")
        report.append(f"- **其他文件**: {structure['other_files']}")
        report.append(f"- **目录数量**: {structure['directories']}")
        report.append("")
        
        # 文档情况
        report.append("## 📚 文档情况")
        report.append("")
        if structure['has_readme']:
            report.append("✅ **README文档**: 已建立")
            report.append(f"- README文件: {', '.join(structure['readme_files'])}")
        else:
            report.append("❌ **README文档**: 未建立")
        report.append("")
        
        # 项目配置
        report.append("## ⚙️ 项目配置")
        report.append("")
        configs = []
        if structure['has_package_json']:
            configs.append("✅ package.json")
        if structure['has_requirements_txt']:
            configs.append("✅ requirements.txt")
        if structure['has_dockerfile']:
            configs.append("✅ Docker配置")
        
        if configs:
            report.append("已配置:")
            for config in configs:
                report.append(f"- {config}")
        else:
            report.append("❌ 未发现标准配置文件")
        report.append("")
        
        # 开发活跃度
        report.append("## 🔄 开发活跃度")
        report.append("")
        report.append(f"- **提交次数**: {git_info['commit_count']}")
        report.append(f"- **贡献者数**: {git_info['contributors']}")
        report.append(f"- **最后提交**: {git_info['last_commit']}")
        report.append("")
        
        # 文件类型分布
        if structure['file_types']:
            report.append("## 📄 文件类型分布")
            report.append("")
            # 按数量排序，显示前10个
            sorted_types = sorted(structure['file_types'].items(), key=lambda x: x[1], reverse=True)[:10]
            for ext, count in sorted_types:
                ext_name = ext if ext else "(无扩展名)"
                report.append(f"- {ext_name}: {count} 个")
            report.append("")
        
        # 评估和建议
        report.append("## 💡 评估和建议")
        report.append("")
        
        score = 0
        suggestions = []
        
        # README评估
        if structure['has_readme']:
            score += 25
            report.append("✅ README文档完善")
        else:
            suggestions.append("添加README.md文档")
        
        # 代码文件评估
        if structure['code_files'] > 0:
            score += 25
            report.append("✅ 包含代码文件")
        else:
            suggestions.append("添加代码文件")
        
        # 配置文件评估
        if structure['has_package_json'] or structure['has_requirements_txt']:
            score += 25
            report.append("✅ 项目配置完善")
        else:
            suggestions.append("添加项目配置文件")
        
        # 开发活跃度评估
        if git_info['commit_count'] > 0:
            score += 25
            report.append("✅ 有开发历史")
        else:
            suggestions.append("开始代码开发")
        
        report.append(f"")
        report.append(f"**项目评分**: {score}/100")
        report.append("")
        
        if suggestions:
            report.append("**改进建议**:")
            for suggestion in suggestions:
                report.append(f"- {suggestion}")
        else:
            report.append("🎉 项目状态良好！")
        
        report.append("")
        report.append("---")
        report.append(f"*分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
        
        return "\n".join(report)


def main():
    parser = argparse.ArgumentParser(
        description="分析项目详细状态",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python analyze_project_status.py /path/to/repos
  python analyze_project_status.py /path/to/repos --output results.json
        """
    )
    
    parser.add_argument(
        'base_dir',
        help='包含Git仓库的基础目录'
    )
    
    parser.add_argument(
        '--output',
        help='输出JSON结果到指定文件'
    )
    
    args = parser.parse_args()
    
    # 创建分析器
    analyzer = ProjectAnalyzer(args.base_dir)
    
    # 分析所有项目
    results = analyzer.analyze_all_projects()
    
    if not results:
        print("未找到任何Git仓库")
        sys.exit(1)
    
    # 输出JSON结果
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"分析结果已保存到: {args.output}")
    
    # 生成每个项目的报告
    for project_key, project_data in results.items():
        report = analyzer.generate_project_report(project_key, project_data)
        
        # 保存到文件
        safe_name = project_key.replace('/', '_').replace('\\', '_')
        report_file = f"project_report_{safe_name}.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"项目报告已生成: {report_file}")
    
    print(f"\n总共分析了 {len(results)} 个项目")


if __name__ == '__main__':
    main() 