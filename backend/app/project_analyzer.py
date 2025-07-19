"""
项目状态分析模块
用于分析本地Git仓库的状态信息
"""

import os
import subprocess
import asyncio
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import logging

from app.config import settings


class ProjectAnalyzer:
    def __init__(self):
        self.repos_dir = Path(settings.local_repos_dir)
        self.setup_logging()
    
    def setup_logging(self):
        """设置日志"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    async def analyze_all_projects(self) -> Dict[str, Dict]:
        """分析所有项目"""
        if not self.repos_dir.exists():
            self.logger.error(f"本地仓库目录不存在: {self.repos_dir}")
            return {}
        
        git_repos = []
        try:
            for git_dir in self.repos_dir.rglob('.git'):
                if git_dir.is_dir():
                    project_dir = git_dir.parent
                    git_repos.append(project_dir)
        except Exception as e:
            self.logger.error(f"查找Git仓库失败: {e}")
            return {}
        
        self.logger.info(f"找到 {len(git_repos)} 个Git仓库")
        
        results = {}
        for repo_path in git_repos:
            relative_path = repo_path.relative_to(self.repos_dir)
            project_key = str(relative_path)
            
            self.logger.info(f"分析项目: {project_key}")
            
            # 分析项目结构
            structure = await self.analyze_project_structure(repo_path)
            
            # 获取Git信息
            git_info = await self.get_git_info(repo_path)
            
            # 计算质量评分
            quality_score = self.calculate_quality_score(structure, git_info)
            
            results[project_key] = {
                'path': str(repo_path),
                'relative_path': str(relative_path),
                'structure': structure,
                'git_info': git_info,
                'quality_score': quality_score,
                'analysis_time': datetime.now().isoformat()
            }
        
        return results
    
    async def analyze_project_structure(self, repo_path: Path) -> Dict:
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
    
    async def get_git_info(self, repo_path: Path) -> Dict:
        """获取Git信息"""
        git_info = {
            'branch': 'unknown',
            'last_commit': 'unknown',
            'commit_count': 0,
            'contributors': 0
        }
        
        try:
            # 获取当前分支
            result = await asyncio.create_subprocess_exec(
                'git', 'branch', '--show-current',
                cwd=repo_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await result.communicate()
            if result.returncode == 0:
                git_info['branch'] = stdout.decode().strip()
            
            # 获取最后提交信息
            result = await asyncio.create_subprocess_exec(
                'git', 'log', '-1', '--format=%H|%an|%ad|%s', '--date=short',
                cwd=repo_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await result.communicate()
            if result.returncode == 0 and stdout.decode().strip():
                parts = stdout.decode().strip().split('|')
                if len(parts) >= 4:
                    git_info['last_commit'] = f"{parts[1]} ({parts[2]}): {parts[3]}"
            
            # 获取提交数量
            result = await asyncio.create_subprocess_exec(
                'git', 'rev-list', '--count', 'HEAD',
                cwd=repo_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await result.communicate()
            if result.returncode == 0:
                git_info['commit_count'] = int(stdout.decode().strip())
            
            # 获取贡献者数量
            result = await asyncio.create_subprocess_exec(
                'git', 'shortlog', '-sn', '--no-merges',
                cwd=repo_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await result.communicate()
            if result.returncode == 0:
                output = stdout.decode().strip()
                git_info['contributors'] = len(output.split('\n')) if output else 0
                
        except Exception as e:
            self.logger.error(f"获取Git信息失败 {repo_path}: {e}")
        
        return git_info
    
    def calculate_quality_score(self, structure: Dict, git_info: Dict) -> int:
        """计算项目质量评分"""
        score = 0
        
        # README评估 (25分)
        if structure['has_readme']:
            score += 25
        
        # 代码文件评估 (25分)
        if structure['code_files'] > 0:
            score += 25
        
        # 配置文件评估 (25分)
        if structure['has_package_json'] or structure['has_requirements_txt']:
            score += 25
        
        # 开发活跃度评估 (25分)
        if git_info['commit_count'] > 0:
            score += 25
        
        return score
    
    async def update_local_repos(self) -> bool:
        """更新本地仓库"""
        if not self.repos_dir.exists():
            self.logger.error(f"本地仓库目录不存在: {self.repos_dir}")
            return False
        
        success_count = 0
        total_count = 0
        
        try:
            for git_dir in self.repos_dir.rglob('.git'):
                if git_dir.is_dir():
                    project_dir = git_dir.parent
                    total_count += 1
                    
                    try:
                        # 执行git pull
                        result = await asyncio.create_subprocess_exec(
                            'git', 'pull',
                            cwd=project_dir,
                            stdout=asyncio.subprocess.PIPE,
                            stderr=asyncio.subprocess.PIPE
                        )
                        stdout, stderr = await result.communicate()
                        
                        if result.returncode == 0:
                            success_count += 1
                            self.logger.info(f"成功更新: {project_dir.name}")
                        else:
                            self.logger.warning(f"更新失败: {project_dir.name} - {stderr.decode()}")
                    
                    except Exception as e:
                        self.logger.error(f"更新异常: {project_dir.name} - {e}")
            
            self.logger.info(f"仓库更新完成: {success_count}/{total_count} 成功")
            return success_count == total_count
            
        except Exception as e:
            self.logger.error(f"更新本地仓库失败: {e}")
            return False 