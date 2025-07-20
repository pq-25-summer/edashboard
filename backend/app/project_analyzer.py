"""
项目状态分析模块
用于分析本地Git仓库的状态信息
"""

import os
import subprocess
import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

from app.config import settings
from app.language_analyzer import LanguageAnalyzer
from app.git_workflow_analyzer import GitWorkflowAnalyzer
from app.database import db


class ProjectAnalyzer:
    def __init__(self):
        self.repos_dir = Path(settings.local_repos_dir)
        self.language_analyzer = LanguageAnalyzer()
        self.git_workflow_analyzer = GitWorkflowAnalyzer(str(self.repos_dir))
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
            
            # 分析技术栈
            tech_stack = self.language_analyzer.analyze_project_tech_stack(repo_path)
            
            # 获取Git信息
            git_info = await self.get_git_info(repo_path)
            
            # 分析Git工作流程
            workflow_info = await self.analyze_git_workflow(project_key, repo_path)
            
            # 分析Issue驱动开发
            issue_driven_info = await self.analyze_issue_driven_development(project_key, repo_path)
            
            # 计算质量评分
            quality_score = self.calculate_quality_score(structure, git_info)
            
            results[project_key] = {
                'path': str(repo_path),
                'relative_path': str(relative_path),
                'structure': structure,
                'tech_stack': tech_stack,
                'git_info': git_info,
                'workflow_info': workflow_info,
                'issue_driven_info': issue_driven_info,
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
    
    async def analyze_git_workflow(self, project_key: str, repo_path: Path) -> Dict:
        """分析Git工作流程"""
        try:
            # 从项目路径提取owner/repo
            parts = project_key.split('/')
            if len(parts) >= 2:
                owner = parts[0]
                repo = parts[1]
                github_url = f"https://github.com/{owner}/{repo}"
                
                # 使用Git工作流程分析器
                workflow_stats = self.git_workflow_analyzer.analyze_project(project_key, github_url)
                
                if workflow_stats:
                    return {
                        'workflow_style': workflow_stats.workflow_style,
                        'workflow_score': workflow_stats.workflow_score,
                        'total_branches': workflow_stats.total_branches,
                        'feature_branches': workflow_stats.feature_branches,
                        'hotfix_branches': workflow_stats.hotfix_branches,
                        'merge_commits': workflow_stats.merge_commits,
                        'rebase_commits': workflow_stats.rebase_commits,
                        'uses_feature_branches': workflow_stats.uses_feature_branches,
                        'uses_main_branch_merges': workflow_stats.uses_main_branch_merges,
                        'uses_rebase': workflow_stats.uses_rebase,
                        'uses_pull_requests': workflow_stats.uses_pull_requests
                    }
                else:
                    self.logger.warning(f"Git工作流程分析失败: {project_key}")
            
        except Exception as e:
            self.logger.error(f"分析Git工作流程失败 {project_key}: {e}")
        
        # 返回默认值
        return {
            'workflow_style': 'Simple (简单模式)',
            'workflow_score': 0.0,
            'total_branches': 0,
            'feature_branches': 0,
            'hotfix_branches': 0,
            'merge_commits': 0,
            'rebase_commits': 0,
            'uses_feature_branches': False,
            'uses_main_branch_merges': False,
            'uses_rebase': False,
            'uses_pull_requests': False
        }
    
    async def analyze_issue_driven_development(self, project_key: str, repo_path: Path) -> Dict:
        """分析Issue驱动开发"""
        try:
            # 从项目路径提取owner/repo
            parts = project_key.split('/')
            if len(parts) >= 2:
                owner = parts[0]
                repo = parts[1]
                github_url = f"https://github.com/{owner}/{repo}"
                
                # 分析Git提交
                commit_stats = await self._analyze_commits_for_issues(repo_path)
                
                # 分析GitHub Issues
                issue_stats = await self._analyze_github_issues(github_url)
                
                # 计算Issue驱动开发指标
                metrics = self._calculate_issue_driven_metrics(commit_stats, issue_stats)
                
                # 计算评分和质量评级
                score, quality = self._calculate_issue_driven_score(metrics)
                
                return {
                    'total_issues': issue_stats['total_issues'],
                    'commits_with_issue_refs': metrics['commits_with_issue_refs'],
                    'commits_without_issue_refs': metrics['commits_without_issue_refs'],
                    'issues_with_assignees': issue_stats['issues_with_assignees'],
                    'issues_without_assignees': issue_stats['issues_without_assignees'],
                    'closed_issues': issue_stats['closed_issues'],
                    'open_issues': issue_stats['open_issues'],
                    'commit_issue_ratio': metrics['commit_issue_ratio'],
                    'issue_assignee_ratio': metrics['issue_assignee_ratio'],
                    'issue_closure_ratio': metrics['issue_closure_ratio'],
                    'uses_issue_driven_development': score >= 60,
                    'issue_driven_score': score,
                    'issue_workflow_quality': quality
                }
            else:
                self.logger.warning(f"项目路径格式不正确: {project_key}")
            
        except Exception as e:
            self.logger.error(f"分析Issue驱动开发失败 {project_key}: {e}")
        
        # 返回默认值
        return {
            'total_issues': 0,
            'commits_with_issue_refs': 0,
            'commits_without_issue_refs': 0,
            'issues_with_assignees': 0,
            'issues_without_assignees': 0,
            'closed_issues': 0,
            'open_issues': 0,
            'commit_issue_ratio': 0.0,
            'issue_assignee_ratio': 0.0,
            'issue_closure_ratio': 0.0,
            'uses_issue_driven_development': False,
            'issue_driven_score': 0.0,
            'issue_workflow_quality': '一般'
        }
    
    async def _analyze_commits_for_issues(self, repo_path: Path) -> Dict:
        """分析Git提交中的issue引用"""
        try:
            # 获取所有提交
            result = await asyncio.create_subprocess_exec(
                'git', 'log', '--pretty=format:%H|%an|%ad|%s', '--date=short',
                cwd=repo_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await result.communicate()
            
            if result.returncode != 0:
                self.logger.warning(f"获取提交历史失败: {stderr.decode()}")
                return self._get_default_commit_stats()
            
            commits = []
            for line in stdout.decode().strip().split('\n'):
                if line.strip():
                    parts = line.split('|')
                    if len(parts) >= 4:
                        commits.append({
                            'hash': parts[0],
                            'author': parts[1],
                            'date': parts[2],
                            'message': parts[3]
                        })
            
            # 分析提交信息中的issue引用
            issue_patterns = [
                r'#(\d+)',  # #123
                r'issue\s*#(\d+)',  # issue #123
                r'fixes?\s*#(\d+)',  # fixes #123
                r'closes?\s*#(\d+)',  # closes #123
                r'resolves?\s*#(\d+)',  # resolves #123
                r'addresses?\s*#(\d+)',  # addresses #123
                r'related\s+to\s*#(\d+)',  # related to #123
                r'see\s*#(\d+)',  # see #123
                r'(\d+)\s*$',  # 123 (行尾)
            ]
            
            commits_with_issue_refs = 0
            for commit in commits:
                for pattern in issue_patterns:
                    import re
                    if re.search(pattern, commit['message'], re.IGNORECASE):
                        commits_with_issue_refs += 1
                        break
            
            return {
                'total_commits': len(commits),
                'commits_with_issue_refs': commits_with_issue_refs,
                'commits_without_issue_refs': len(commits) - commits_with_issue_refs
            }
            
        except Exception as e:
            self.logger.error(f"分析提交失败: {e}")
            return self._get_default_commit_stats()
    
    async def _analyze_github_issues(self, github_url: str) -> Dict:
        """分析GitHub Issues"""
        try:
            # 从数据库获取issue数据
            async with db.get_db() as conn:
                async with conn.cursor() as cur:
                    # 查找项目ID
                    await cur.execute(
                        "SELECT id FROM projects WHERE github_url = %s",
                        (github_url,)
                    )
                    project_result = await cur.fetchone()
                    
                    if not project_result:
                        self.logger.warning(f"项目不存在: {github_url}")
                        return self._get_default_issue_stats()
                    
                    project_id = project_result['id']
                    
                    # 获取所有issues
                    await cur.execute("""
                        SELECT i.*, s.name as student_name, s.github_username
                        FROM issues i
                        LEFT JOIN students s ON i.student_id = s.id
                        WHERE i.project_id = %s
                        ORDER BY i.created_at DESC
                    """, (project_id,))
                    
                    issues = await cur.fetchall()
                    
                    # 分析issue数据
                    issues_with_assignees = 0
                    issues_without_assignees = 0
                    closed_issues = 0
                    open_issues = 0
                    
                    for issue in issues:
                        if issue['state'] == 'closed':
                            closed_issues += 1
                        else:
                            open_issues += 1
                        
                        # 检查是否有assignee（通过学生关联）
                        if issue['student_id']:
                            issues_with_assignees += 1
                        else:
                            issues_without_assignees += 1
                    
                    return {
                        'total_issues': len(issues),
                        'issues_with_assignees': issues_with_assignees,
                        'issues_without_assignees': issues_without_assignees,
                        'closed_issues': closed_issues,
                        'open_issues': open_issues
                    }
                    
        except Exception as e:
            self.logger.error(f"分析GitHub Issues失败: {e}")
            return self._get_default_issue_stats()
    
    def _calculate_issue_driven_metrics(self, commit_stats: Dict, issue_stats: Dict) -> Dict:
        """计算Issue驱动开发指标"""
        total_commits = commit_stats['total_commits']
        total_issues = issue_stats['total_issues']
        commits_with_issue_refs = commit_stats['commits_with_issue_refs']
        issues_with_assignees = issue_stats['issues_with_assignees']
        closed_issues = issue_stats['closed_issues']
        
        # 计算比例
        commit_issue_ratio = (commits_with_issue_refs / total_commits * 100) if total_commits > 0 else 0
        issue_assignee_ratio = (issues_with_assignees / total_issues * 100) if total_issues > 0 else 0
        issue_closure_ratio = (closed_issues / total_issues * 100) if total_issues > 0 else 0
        
        return {
            'commits_with_issue_refs': commits_with_issue_refs,
            'commits_without_issue_refs': total_commits - commits_with_issue_refs,
            'commit_issue_ratio': commit_issue_ratio,
            'issue_assignee_ratio': issue_assignee_ratio,
            'issue_closure_ratio': issue_closure_ratio
        }
    
    def _calculate_issue_driven_score(self, metrics: Dict) -> tuple:
        """计算Issue驱动开发评分"""
        score = 0.0
        
        # 提交-Issue关联度 (40分)
        commit_issue_ratio = metrics['commit_issue_ratio']
        if commit_issue_ratio >= 80:
            score += 40
        elif commit_issue_ratio >= 60:
            score += 30
        elif commit_issue_ratio >= 40:
            score += 20
        elif commit_issue_ratio >= 20:
            score += 10
        
        # Issue有assignee的比例 (30分)
        issue_assignee_ratio = metrics['issue_assignee_ratio']
        if issue_assignee_ratio >= 80:
            score += 30
        elif issue_assignee_ratio >= 60:
            score += 25
        elif issue_assignee_ratio >= 40:
            score += 20
        elif issue_assignee_ratio >= 20:
            score += 15
        
        # Issue关闭比例 (20分)
        issue_closure_ratio = metrics['issue_closure_ratio']
        if issue_closure_ratio >= 80:
            score += 20
        elif issue_closure_ratio >= 60:
            score += 15
        elif issue_closure_ratio >= 40:
            score += 10
        elif issue_closure_ratio >= 20:
            score += 5
        
        # Issue数量 (10分)
        score += 10
        
        # 确定质量评级
        if score >= 80:
            quality = "优秀"
        elif score >= 60:
            quality = "良好"
        elif score >= 40:
            quality = "一般"
        elif score >= 20:
            quality = "较差"
        else:
            quality = "很差"
        
        return score, quality
    
    def _get_default_commit_stats(self) -> Dict:
        """获取默认提交统计"""
        return {
            'total_commits': 0,
            'commits_with_issue_refs': 0,
            'commits_without_issue_refs': 0
        }
    
    def _get_default_issue_stats(self) -> Dict:
        """获取默认Issue统计"""
        return {
            'total_issues': 0,
            'issues_with_assignees': 0,
            'issues_without_assignees': 0,
            'closed_issues': 0,
            'open_issues': 0
        }
    
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
    
    async def check_repos_need_update(self) -> Dict[str, bool]:
        """检查哪些仓库需要更新"""
        if not self.repos_dir.exists():
            self.logger.error(f"本地仓库目录不存在: {self.repos_dir}")
            return {}
        
        update_status = {}
        
        try:
            for git_dir in self.repos_dir.rglob('.git'):
                if git_dir.is_dir():
                    project_dir = git_dir.parent
                    project_key = str(project_dir.relative_to(self.repos_dir))
                    
                    try:
                        # 检查是否有远程更新
                        result = await asyncio.create_subprocess_exec(
                            'git', 'fetch', 'origin',
                            cwd=project_dir,
                            stdout=asyncio.subprocess.PIPE,
                            stderr=asyncio.subprocess.PIPE
                        )
                        await result.communicate()
                        
                        if result.returncode == 0:
                            # 检查是否有新的提交
                            log_result = await asyncio.create_subprocess_exec(
                                'git', 'log', 'HEAD..origin/main', '--oneline',
                                cwd=project_dir,
                                stdout=asyncio.subprocess.PIPE,
                                stderr=asyncio.subprocess.PIPE
                            )
                            stdout, stderr = await log_result.communicate()
                            
                            has_updates = bool(stdout.decode().strip())
                            update_status[project_key] = has_updates
                            
                            if has_updates:
                                self.logger.info(f"仓库需要更新: {project_key}")
                        else:
                            update_status[project_key] = False
                            self.logger.warning(f"检查更新失败: {project_key}")
                    
                    except Exception as e:
                        self.logger.error(f"检查更新异常: {project_key} - {e}")
                        update_status[project_key] = False
            
            self.logger.info(f"仓库更新检查完成: {sum(update_status.values())}/{len(update_status)} 需要更新")
            return update_status
            
        except Exception as e:
            self.logger.error(f"检查仓库更新失败: {e}")
            return {}
    
    async def get_last_sync_info(self) -> Dict[str, Any]:
        """获取最后同步信息"""
        try:
            async with db.get_db() as conn:
                async with conn.cursor() as cur:
                    await cur.execute("""
                        SELECT sync_time, total_projects, successful_syncs, 
                               failed_syncs, projects_with_changes
                        FROM git_sync_logs
                        ORDER BY sync_time DESC
                        LIMIT 1
                    """)
                    result = await cur.fetchone()
                    
                    if result:
                        return {
                            'last_sync_time': result['sync_time'],
                            'total_projects': result['total_projects'],
                            'successful_syncs': result['successful_syncs'],
                            'failed_syncs': result['failed_syncs'],
                            'projects_with_changes': result['projects_with_changes']
                        }
                    else:
                        return {
                            'last_sync_time': None,
                            'total_projects': 0,
                            'successful_syncs': 0,
                            'failed_syncs': 0,
                            'projects_with_changes': 0
                        }
        except Exception as e:
            self.logger.error(f"获取同步信息失败: {e}")
            return {} 