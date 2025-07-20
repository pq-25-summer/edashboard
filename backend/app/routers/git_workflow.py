#!/usr/bin/env python3
"""
Git工作流程分析API路由
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Optional
from datetime import datetime
import logging

from ..database import db
from ..git_workflow_analyzer import GitWorkflowAnalyzer, GitWorkflowStats
from ..models import Project
from ..config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/git-workflow", tags=["git-workflow"])


@router.get("/summary")
async def get_git_workflow_summary():
    """获取Git工作流程分析摘要"""
    try:
        # 从数据库获取项目列表
        async with db.get_db() as conn:
            async with conn.cursor() as cur:
                await cur.execute("SELECT name, github_url FROM projects")
                projects_result = await cur.fetchall()
                projects = [{"name": row["name"], "github_url": row["github_url"]} for row in projects_result]
        
        # 分析所有项目
        analyzer = GitWorkflowAnalyzer(str(settings.local_repos_dir))
        results = analyzer.analyze_all_projects(projects)
        
        if not results:
            return {
                "total_projects": 0,
                "workflow_statistics": {},
                "message": "没有找到可分析的项目"
            }
        
        # 计算统计信息
        total_projects = len(results)
        workflow_styles = {}
        feature_branch_usage = 0
        merge_usage = 0
        rebase_usage = 0
        pr_usage = 0
        total_score = 0
        
        for result in results:
            # 工作流程风格统计
            style = result.workflow_style
            workflow_styles[style] = workflow_styles.get(style, 0) + 1
            
            # 功能使用统计
            if result.uses_feature_branches:
                feature_branch_usage += 1
            if result.uses_main_branch_merges:
                merge_usage += 1
            if result.uses_rebase:
                rebase_usage += 1
            if result.uses_pull_requests:
                pr_usage += 1
            
            total_score += result.workflow_score
        
        avg_score = total_score / total_projects if total_projects > 0 else 0
        
        return {
            "total_projects": total_projects,
            "workflow_statistics": {
                "workflow_styles": workflow_styles,
                "feature_branch_usage": {
                    "count": feature_branch_usage,
                    "percentage": round(feature_branch_usage / total_projects * 100, 1) if total_projects > 0 else 0
                },
                "merge_usage": {
                    "count": merge_usage,
                    "percentage": round(merge_usage / total_projects * 100, 1) if total_projects > 0 else 0
                },
                "rebase_usage": {
                    "count": rebase_usage,
                    "percentage": round(rebase_usage / total_projects * 100, 1) if total_projects > 0 else 0
                },
                "pull_request_usage": {
                    "count": pr_usage,
                    "percentage": round(pr_usage / total_projects * 100, 1) if total_projects > 0 else 0
                },
                "average_score": round(avg_score, 1)
            },
            "analysis_time": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"获取Git工作流程摘要时出错: {e}")
        raise HTTPException(status_code=500, detail=f"分析失败: {str(e)}")


@router.get("/projects")
async def get_git_workflow_projects():
    """获取所有项目的Git工作流程分析结果"""
    try:
        # 从数据库获取项目列表
        async with db.get_db() as conn:
            async with conn.cursor() as cur:
                await cur.execute("SELECT name, github_url FROM projects")
                projects_result = await cur.fetchall()
                projects = [{"name": row["name"], "github_url": row["github_url"]} for row in projects_result]
        
        # 分析所有项目
        analyzer = GitWorkflowAnalyzer(str(settings.local_repos_dir))
        results = analyzer.analyze_all_projects(projects)
        
        # 转换为字典格式
        projects_data = []
        for result in results:
            projects_data.append({
                "project_name": result.project_name,
                "github_url": result.github_url,
                "total_branches": result.total_branches,
                "main_branch_name": result.main_branch_name,
                "feature_branches": result.feature_branches,
                "hotfix_branches": result.hotfix_branches,
                "total_commits": result.total_commits,
                "commits_on_main": result.commits_on_main,
                "commits_on_branches": result.commits_on_branches,
                "merge_commits": result.merge_commits,
                "rebase_commits": result.rebase_commits,
                "has_pull_requests": result.has_pull_requests,
                "pull_request_count": result.pull_request_count,
                "merged_pull_requests": result.merged_pull_requests,
                "uses_feature_branches": result.uses_feature_branches,
                "uses_main_branch_merges": result.uses_main_branch_merges,
                "uses_rebase": result.uses_rebase,
                "uses_pull_requests": result.uses_pull_requests,
                "workflow_score": result.workflow_score,
                "workflow_style": result.workflow_style,
                "analyzed_at": result.analyzed_at.isoformat()
            })
        
        # 按评分排序
        projects_data.sort(key=lambda x: x["workflow_score"], reverse=True)
        
        return {
            "projects": projects_data,
            "total_projects": len(projects_data),
            "analysis_time": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"获取项目Git工作流程时出错: {e}")
        raise HTTPException(status_code=500, detail=f"分析失败: {str(e)}")


@router.get("/projects/{project_name}")
async def get_project_git_workflow(project_name: str):
    """获取指定项目的Git工作流程分析结果"""
    try:
        # 从数据库获取项目信息
        async with db.get_db() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "SELECT name, github_url FROM projects WHERE name = %s",
                    (project_name,)
                )
                project_result = await cur.fetchone()
                
                if not project_result:
                    raise HTTPException(status_code=404, detail=f"项目 {project_name} 不存在")
        
        # 分析项目
        analyzer = GitWorkflowAnalyzer(str(settings.local_repos_dir))
        result = analyzer.analyze_project(
            project_result["name"],
            project_result["github_url"]
        )
        
        if not result:
            raise HTTPException(status_code=404, detail=f"无法分析项目 {project_name}")
        
        return {
            "project_name": result.project_name,
            "github_url": result.github_url,
            "total_branches": result.total_branches,
            "main_branch_name": result.main_branch_name,
            "feature_branches": result.feature_branches,
            "hotfix_branches": result.hotfix_branches,
            "total_commits": result.total_commits,
            "commits_on_main": result.commits_on_main,
            "commits_on_branches": result.commits_on_branches,
            "merge_commits": result.merge_commits,
            "rebase_commits": result.rebase_commits,
            "has_pull_requests": result.has_pull_requests,
            "pull_request_count": result.pull_request_count,
            "merged_pull_requests": result.merged_pull_requests,
            "uses_feature_branches": result.uses_feature_branches,
            "uses_main_branch_merges": result.uses_main_branch_merges,
            "uses_rebase": result.uses_rebase,
            "uses_pull_requests": result.uses_pull_requests,
            "workflow_score": result.workflow_score,
            "workflow_style": result.workflow_style,
            "analyzed_at": result.analyzed_at.isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取项目 {project_name} Git工作流程时出错: {e}")
        raise HTTPException(status_code=500, detail=f"分析失败: {str(e)}")


@router.post("/analyze")
async def analyze_git_workflow():
    """手动触发Git工作流程分析"""
    try:
        # 从数据库获取项目列表
        async with db.get_db() as conn:
            async with conn.cursor() as cur:
                await cur.execute("SELECT name, github_url FROM projects")
                projects_result = await cur.fetchall()
                projects = [{"name": row["name"], "github_url": row["github_url"]} for row in projects_result]
        
        # 分析所有项目
        analyzer = GitWorkflowAnalyzer(str(settings.local_repos_dir))
        results = analyzer.analyze_all_projects(projects)
        
        return {
            "message": "Git工作流程分析完成",
            "analyzed_projects": len(results),
            "total_projects": len(projects),
            "analysis_time": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Git工作流程分析时出错: {e}")
        raise HTTPException(status_code=500, detail=f"分析失败: {str(e)}")


@router.get("/statistics")
async def get_git_workflow_statistics():
    """获取详细的Git工作流程统计信息"""
    try:
        # 从数据库获取项目列表
        async with db.get_db() as conn:
            async with conn.cursor() as cur:
                await cur.execute("SELECT name, github_url FROM projects")
                projects_result = await cur.fetchall()
                projects = [{"name": row["name"], "github_url": row["github_url"]} for row in projects_result]
        
        # 分析所有项目
        analyzer = GitWorkflowAnalyzer(str(settings.local_repos_dir))
        results = analyzer.analyze_all_projects(projects)
        
        if not results:
            return {
                "total_projects": 0,
                "statistics": {},
                "message": "没有找到可分析的项目"
            }
        
        # 详细统计
        total_projects = len(results)
        workflow_styles = {}
        score_ranges = {
            "优秀 (80-100分)": 0,
            "良好 (60-79分)": 0,
            "一般 (40-59分)": 0,
            "简单 (20-39分)": 0,
            "基础 (0-19分)": 0
        }
        
        feature_branch_projects = []
        merge_projects = []
        rebase_projects = []
        pr_projects = []
        
        total_score = 0
        total_commits = 0
        total_branches = 0
        
        for result in results:
            # 工作流程风格统计
            style = result.workflow_style
            workflow_styles[style] = workflow_styles.get(style, 0) + 1
            
            # 评分范围统计
            score = result.workflow_score
            total_score += score
            
            if score >= 80:
                score_ranges["优秀 (80-100分)"] += 1
            elif score >= 60:
                score_ranges["良好 (60-79分)"] += 1
            elif score >= 40:
                score_ranges["一般 (40-59分)"] += 1
            elif score >= 20:
                score_ranges["简单 (20-39分)"] += 1
            else:
                score_ranges["基础 (0-19分)"] += 1
            
            # 功能使用项目列表
            if result.uses_feature_branches:
                feature_branch_projects.append(result.project_name)
            if result.uses_main_branch_merges:
                merge_projects.append(result.project_name)
            if result.uses_rebase:
                rebase_projects.append(result.project_name)
            if result.uses_pull_requests:
                pr_projects.append(result.project_name)
            
            # 累计统计
            total_commits += result.total_commits
            total_branches += result.total_branches
        
        avg_score = total_score / total_projects if total_projects > 0 else 0
        avg_commits = total_commits / total_projects if total_projects > 0 else 0
        avg_branches = total_branches / total_projects if total_projects > 0 else 0
        
        return {
            "total_projects": total_projects,
            "statistics": {
                "workflow_styles": workflow_styles,
                "score_ranges": score_ranges,
                "average_score": round(avg_score, 1),
                "average_commits": round(avg_commits, 1),
                "average_branches": round(avg_branches, 1),
                "feature_branch_projects": {
                    "count": len(feature_branch_projects),
                    "percentage": round(len(feature_branch_projects) / total_projects * 100, 1),
                    "projects": feature_branch_projects
                },
                "merge_projects": {
                    "count": len(merge_projects),
                    "percentage": round(len(merge_projects) / total_projects * 100, 1),
                    "projects": merge_projects
                },
                "rebase_projects": {
                    "count": len(rebase_projects),
                    "percentage": round(len(rebase_projects) / total_projects * 100, 1),
                    "projects": rebase_projects
                },
                "pull_request_projects": {
                    "count": len(pr_projects),
                    "percentage": round(len(pr_projects) / total_projects * 100, 1),
                    "projects": pr_projects
                }
            },
            "analysis_time": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"获取Git工作流程统计时出错: {e}")
        raise HTTPException(status_code=500, detail=f"统计失败: {str(e)}") 