#!/usr/bin/env python3
"""
Git工作流程分析器
分析项目的Git使用风格，包括分支使用、合并模式、Pull Request等
"""

import os
import subprocess
import re
import json
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class GitWorkflowStats:
    """Git工作流程统计信息"""
    project_name: str
    github_url: str
    
    # 分支使用情况
    total_branches: int
    main_branch_name: str
    feature_branches: int
    hotfix_branches: int
    
    # 提交模式
    total_commits: int
    commits_on_main: int
    commits_on_branches: int
    merge_commits: int
    rebase_commits: int
    
    # Pull Request使用情况
    has_pull_requests: bool
    pull_request_count: int
    merged_pull_requests: int
    
    # 工作流程特征
    uses_feature_branches: bool
    uses_main_branch_merges: bool
    uses_rebase: bool
    uses_pull_requests: bool
    
    # 评分
    workflow_score: float
    workflow_style: str
    
    # 分析时间
    analyzed_at: datetime


class GitWorkflowAnalyzer:
    """Git工作流程分析器"""
    
    def __init__(self, projects_base_path: str = "repos"):
        self.projects_base_path = Path(projects_base_path)
        self.main_branch_names = ['main', 'master', 'develop']
    
    def analyze_project(self, project_name: str, github_url: str) -> Optional[GitWorkflowStats]:
        """分析单个项目的Git工作流程"""
        try:
            repo_path = self._get_repo_path(project_name, github_url)
            if not repo_path.exists():
                logger.warning(f"仓库路径不存在: {repo_path}")
                return None
            
            # 生成唯一的项目名称
            unique_project_name = self._generate_unique_project_name(project_name, github_url)
            
            logger.info(f"开始分析项目: {unique_project_name}")
            
            # 分析分支使用情况
            branch_stats = self._analyze_branches(repo_path)
            
            # 分析提交模式
            commit_stats = self._analyze_commits(repo_path)
            
            # 分析Pull Request使用情况
            pr_stats = self._analyze_pull_requests(github_url)
            
            # 计算工作流程特征
            workflow_features = self._calculate_workflow_features(
                branch_stats, commit_stats, pr_stats
            )
            
            # 计算评分和工作流程风格
            score, style = self._calculate_workflow_score(workflow_features)
            
            return GitWorkflowStats(
                project_name=unique_project_name,
                github_url=github_url,
                total_branches=branch_stats['total_branches'],
                main_branch_name=branch_stats['main_branch'],
                feature_branches=branch_stats['feature_branches'],
                hotfix_branches=branch_stats['hotfix_branches'],
                total_commits=commit_stats['total_commits'],
                commits_on_main=commit_stats['commits_on_main'],
                commits_on_branches=commit_stats['commits_on_branches'],
                merge_commits=commit_stats['merge_commits'],
                rebase_commits=commit_stats['rebase_commits'],
                has_pull_requests=pr_stats['has_pull_requests'],
                pull_request_count=pr_stats['pull_request_count'],
                merged_pull_requests=pr_stats['merged_pull_requests'],
                uses_feature_branches=workflow_features['uses_feature_branches'],
                uses_main_branch_merges=workflow_features['uses_main_branch_merges'],
                uses_rebase=workflow_features['uses_rebase'],
                uses_pull_requests=workflow_features['uses_pull_requests'],
                workflow_score=score,
                workflow_style=style,
                analyzed_at=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"分析项目 {project_name} 时出错: {e}")
            return None
    
    def _generate_unique_project_name(self, project_name: str, github_url: str) -> str:
        """生成唯一的项目名称"""
        # 从GitHub URL提取owner
        owner = self._extract_owner_from_url(github_url)
        
        # 如果项目名称已经包含owner信息，直接返回
        if '/' in project_name:
            return project_name
        
        # 否则组合owner和项目名称
        return f"{owner}/{project_name}"
    
    def _extract_owner_from_url(self, github_url: str) -> str:
        """从GitHub URL提取owner"""
        if '/orgs/' in github_url:
            # 处理组织仓库的特殊情况
            parts = github_url.split('/')
            if len(parts) >= 6:
                return parts[4]  # orgs
            else:
                return "unknown"
        else:
            # 标准格式: https://github.com/owner/repo
            parts = github_url.rstrip('/').split('/')
            if len(parts) >= 2:
                return parts[-2]
            else:
                return "unknown"
    
    def _get_repo_path(self, project_name: str, github_url: str) -> Path:
        """获取仓库本地路径"""
        # 从GitHub URL提取owner/repo
        if '/orgs/' in github_url:
            # 处理组织仓库的特殊情况
            parts = github_url.split('/')
            if len(parts) >= 6:
                owner = parts[4]  # orgs
                repo = parts[5]   # 组织名
            else:
                owner = "unknown"
                repo = project_name
        else:
            # 标准格式: https://github.com/owner/repo
            parts = github_url.rstrip('/').split('/')
            if len(parts) >= 2:
                owner = parts[-2]
                repo = parts[-1]
            else:
                owner = "unknown"
                repo = project_name
        
        return self.projects_base_path / owner / repo
    
    def _analyze_branches(self, repo_path: Path) -> Dict:
        """分析分支使用情况"""
        try:
            # 获取所有分支
            result = subprocess.run(
                ['git', 'branch', '-a'],
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                logger.warning(f"获取分支失败: {result.stderr}")
                return self._get_default_branch_stats()
            
            branches = result.stdout.strip().split('\n')
            local_branches = []
            remote_branches = []
            
            for branch in branches:
                branch = branch.strip()
                if not branch:
                    continue
                
                if branch.startswith('*'):
                    branch = branch[2:].strip()
                
                if branch.startswith('remotes/'):
                    remote_branches.append(branch.replace('remotes/origin/', ''))
                else:
                    local_branches.append(branch)
            
            # 确定主分支
            main_branch = self._identify_main_branch(local_branches)
            
            # 统计功能分支和热修复分支
            feature_branches = len([b for b in local_branches if self._is_feature_branch(b)])
            hotfix_branches = len([b for b in local_branches if self._is_hotfix_branch(b)])
            
            return {
                'total_branches': len(local_branches),
                'main_branch': main_branch,
                'feature_branches': feature_branches,
                'hotfix_branches': hotfix_branches,
                'local_branches': local_branches,
                'remote_branches': remote_branches
            }
            
        except Exception as e:
            logger.error(f"分析分支时出错: {e}")
            return self._get_default_branch_stats()
    
    def _analyze_commits(self, repo_path: Path) -> Dict:
        """分析提交模式"""
        try:
            # 获取提交统计
            result = subprocess.run(
                ['git', 'log', '--oneline', '--all'],
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                logger.warning(f"获取提交历史失败: {result.stderr}")
                return self._get_default_commit_stats()
            
            commits = result.stdout.strip().split('\n')
            total_commits = len([c for c in commits if c.strip()])
            
            # 获取合并提交
            merge_result = subprocess.run(
                ['git', 'log', '--merges', '--oneline'],
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            merge_commits = 0
            if merge_result.returncode == 0:
                merge_commits = len([c for c in merge_result.stdout.strip().split('\n') if c.strip()])
            
            # 获取rebase提交（通过查找rebase相关的提交信息）
            rebase_result = subprocess.run(
                ['git', 'log', '--grep=rebase', '--oneline'],
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            rebase_commits = 0
            if rebase_result.returncode == 0:
                rebase_commits = len([c for c in rebase_result.stdout.strip().split('\n') if c.strip()])
            
            # 估算主分支提交数（简化处理）
            commits_on_main = max(0, total_commits - merge_commits)
            commits_on_branches = merge_commits
            
            return {
                'total_commits': total_commits,
                'commits_on_main': commits_on_main,
                'commits_on_branches': commits_on_branches,
                'merge_commits': merge_commits,
                'rebase_commits': rebase_commits
            }
            
        except Exception as e:
            logger.error(f"分析提交时出错: {e}")
            return self._get_default_commit_stats()
    
    def _analyze_pull_requests(self, github_url: str) -> Dict:
        """分析Pull Request使用情况"""
        try:
            # 这里简化处理，实际应该通过GitHub API获取PR信息
            # 由于需要GitHub token，暂时返回默认值
            return {
                'has_pull_requests': False,
                'pull_request_count': 0,
                'merged_pull_requests': 0
            }
        except Exception as e:
            logger.error(f"分析Pull Request时出错: {e}")
            return {
                'has_pull_requests': False,
                'pull_request_count': 0,
                'merged_pull_requests': 0
            }
    
    def _identify_main_branch(self, branches: List[str]) -> str:
        """识别主分支"""
        for branch in branches:
            if branch in self.main_branch_names:
                return branch
        return 'main'  # 默认
    
    def _is_feature_branch(self, branch: str) -> bool:
        """判断是否为功能分支"""
        feature_patterns = [
            r'feature/',
            r'feat/',
            r'feature-',
            r'feat-',
            r'dev/',
            r'develop/',
            r'development/'
        ]
        return any(re.search(pattern, branch, re.IGNORECASE) for pattern in feature_patterns)
    
    def _is_hotfix_branch(self, branch: str) -> bool:
        """判断是否为热修复分支"""
        hotfix_patterns = [
            r'hotfix/',
            r'hotfix-',
            r'fix/',
            r'bugfix/',
            r'patch/'
        ]
        return any(re.search(pattern, branch, re.IGNORECASE) for pattern in hotfix_patterns)
    
    def _calculate_workflow_features(self, branch_stats: Dict, commit_stats: Dict, pr_stats: Dict) -> Dict:
        """计算工作流程特征"""
        return {
            'uses_feature_branches': branch_stats['feature_branches'] > 0,
            'uses_main_branch_merges': commit_stats['merge_commits'] > 0,
            'uses_rebase': commit_stats['rebase_commits'] > 0,
            'uses_pull_requests': pr_stats['has_pull_requests']
        }
    
    def _calculate_workflow_score(self, features: Dict) -> Tuple[float, str]:
        """计算工作流程评分和风格"""
        score = 0.0
        style_points = []
        
        # 使用功能分支 +20分
        if features['uses_feature_branches']:
            score += 20
            style_points.append("功能分支开发")
        
        # 使用合并提交 +15分
        if features['uses_main_branch_merges']:
            score += 15
            style_points.append("分支合并")
        
        # 使用rebase +10分
        if features['uses_rebase']:
            score += 10
            style_points.append("Rebase操作")
        
        # 使用Pull Request +25分
        if features['uses_pull_requests']:
            score += 25
            style_points.append("Pull Request")
        
        # 确定工作流程风格
        if score >= 60:
            style = "Git Flow (完整工作流)"
        elif score >= 40:
            style = "Feature Branch (功能分支)"
        elif score >= 20:
            style = "Trunk Based (主干开发)"
        else:
            style = "Simple (简单模式)"
        
        return min(score, 100.0), style
    
    def _get_default_branch_stats(self) -> Dict:
        """获取默认分支统计"""
        return {
            'total_branches': 1,
            'main_branch': 'main',
            'feature_branches': 0,
            'hotfix_branches': 0,
            'local_branches': ['main'],
            'remote_branches': []
        }
    
    def _get_default_commit_stats(self) -> Dict:
        """获取默认提交统计"""
        return {
            'total_commits': 0,
            'commits_on_main': 0,
            'commits_on_branches': 0,
            'merge_commits': 0,
            'rebase_commits': 0
        }
    
    def analyze_all_projects(self, projects: List[Dict]) -> List[GitWorkflowStats]:
        """分析所有项目"""
        results = []
        
        for project in projects:
            stats = self.analyze_project(
                project['name'],
                project['github_url']
            )
            if stats:
                results.append(stats)
        
        return results 