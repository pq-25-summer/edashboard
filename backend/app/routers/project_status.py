"""
项目状态API路由
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
from datetime import datetime
import psycopg

from app.database import get_db, db
from app.models import ProjectStatus, ProjectStatusSummary

router = APIRouter(prefix="/project-status", tags=["项目状态"])


@router.get("/", response_model=List[ProjectStatus])
async def get_all_project_statuses():
    """获取所有项目状态"""
    async with db.get_db() as conn:
        return await _get_all_project_statuses_internal(conn)


async def _get_all_project_statuses_internal(db: psycopg.AsyncConnection):
    """内部函数：获取所有项目状态"""
    async with db.cursor() as cur:
        await cur.execute("""
            SELECT ps.*, p.name as project_name, p.github_url
            FROM project_statuses ps
            JOIN projects p ON ps.project_id = p.id
            ORDER BY ps.quality_score DESC, p.name
        """)
        results = await cur.fetchall()
        
        # 调试信息
        print(f"API查询结果数量: {len(results)}")
        if results:
            first_row = results[0]
            print(f"第一个记录的project_name: {first_row['project_name']}")
            print(f"第一个记录的github_url: {first_row['github_url']}")
        
        project_statuses = []
        for row in results:
            project_statuses.append({
                "id": row["id"],
                "project_id": row["project_id"],
                "has_readme": row["has_readme"],
                "readme_files": row["readme_files"] or [],
                "total_files": row["total_files"],
                "code_files": row["code_files"],
                "doc_files": row["doc_files"],
                "config_files": row["config_files"],
                "project_size_kb": row["project_size_kb"],
                "main_language": row["main_language"],
                "commit_count": row["commit_count"],
                "contributors": row["contributors"],
                "last_commit": row["last_commit"],
                "current_branch": row["current_branch"],
                "has_package_json": row["has_package_json"],
                "has_requirements_txt": row["has_requirements_txt"],
                "has_dockerfile": row["has_dockerfile"],
                "quality_score": row["quality_score"],
                # Git工作流程相关字段
                "workflow_style": row.get("workflow_style"),
                "workflow_score": float(row.get("workflow_score", 0)),
                "total_branches": row.get("total_branches", 0),
                "feature_branches": row.get("feature_branches", 0),
                "hotfix_branches": row.get("hotfix_branches", 0),
                "merge_commits": row.get("merge_commits", 0),
                "rebase_commits": row.get("rebase_commits", 0),
                "uses_feature_branches": row.get("uses_feature_branches", False),
                "uses_main_branch_merges": row.get("uses_main_branch_merges", False),
                "uses_rebase": row.get("uses_rebase", False),
                "uses_pull_requests": row.get("uses_pull_requests", False),
                "created_at": row["created_at"],
                "updated_at": row["updated_at"],
                "project_name": row["project_name"],
                "github_url": row["github_url"]
            })
        
        return project_statuses


@router.get("/{project_id}", response_model=ProjectStatus)
async def get_project_status(project_id: int, db=Depends(get_db)):
    """获取单个项目状态"""
    async with db.cursor() as cur:
        await cur.execute("""
            SELECT ps.*, p.name as project_name, p.github_url
            FROM project_statuses ps
            JOIN projects p ON ps.project_id = p.id
            WHERE ps.project_id = %s
        """, (project_id,))
        result = await cur.fetchone()
        
        if not result:
            raise HTTPException(status_code=404, detail="项目状态未找到")
        
        return {
            "id": result["id"],
            "project_id": result["project_id"],
            "has_readme": result["has_readme"],
            "readme_files": result["readme_files"] or [],
            "total_files": result["total_files"],
            "code_files": result["code_files"],
            "doc_files": result["doc_files"],
            "config_files": result["config_files"],
            "project_size_kb": result["project_size_kb"],
            "main_language": result["main_language"],
            "commit_count": result["commit_count"],
            "contributors": result["contributors"],
            "last_commit": result["last_commit"],
            "current_branch": result["current_branch"],
            "has_package_json": result["has_package_json"],
            "has_requirements_txt": result["has_requirements_txt"],
            "has_dockerfile": result["has_dockerfile"],
            "quality_score": result["quality_score"],
            # Git工作流程相关字段
            "workflow_style": result.get("workflow_style"),
            "workflow_score": float(result.get("workflow_score", 0)),
            "total_branches": result.get("total_branches", 0),
            "feature_branches": result.get("feature_branches", 0),
            "hotfix_branches": result.get("hotfix_branches", 0),
            "merge_commits": result.get("merge_commits", 0),
            "rebase_commits": result.get("rebase_commits", 0),
            "uses_feature_branches": result.get("uses_feature_branches", False),
            "uses_main_branch_merges": result.get("uses_main_branch_merges", False),
            "uses_rebase": result.get("uses_rebase", False),
            "uses_pull_requests": result.get("uses_pull_requests", False),
            "created_at": result["created_at"],
            "updated_at": result["updated_at"],
            "project_name": result["project_name"],
            "github_url": result["github_url"]
        }


@router.get("/summary/overview", response_model=ProjectStatusSummary)
async def get_project_status_summary(db=Depends(get_db)):
    """获取项目状态总览"""
    async with db.cursor() as cur:
        # 获取基本统计
        await cur.execute("SELECT COUNT(*) as total FROM project_statuses")
        total_projects = (await cur.fetchone())["total"]
        
        await cur.execute("SELECT COUNT(*) as count FROM project_statuses WHERE has_readme = true")
        projects_with_readme = (await cur.fetchone())["count"]
        
        readme_coverage = round(projects_with_readme / total_projects * 100, 1) if total_projects > 0 else 0
        
        # 获取平均质量评分
        await cur.execute("SELECT AVG(quality_score) as avg_score FROM project_statuses")
        avg_quality_score = (await cur.fetchone())["avg_score"] or 0
        
        # 获取语言分布
        await cur.execute("""
            SELECT main_language, COUNT(*) as count
            FROM project_statuses
            WHERE main_language IS NOT NULL
            GROUP BY main_language
            ORDER BY count DESC
        """)
        language_results = await cur.fetchall()
        language_distribution = {row["main_language"]: row["count"] for row in language_results}
        
        # 获取平均项目大小
        await cur.execute("SELECT AVG(project_size_kb) as avg_size FROM project_statuses")
        avg_project_size = (await cur.fetchone())["avg_size"] or 0
        
        # 获取平均提交次数
        await cur.execute("SELECT AVG(commit_count) as avg_commits FROM project_statuses")
        avg_commit_count = (await cur.fetchone())["avg_commits"] or 0
        
        # 获取平均贡献者数
        await cur.execute("SELECT AVG(contributors) as avg_contributors FROM project_statuses")
        avg_contributors = (await cur.fetchone())["avg_contributors"] or 0
        
        # 获取按评分分组的项目数
        await cur.execute("""
            SELECT 
                CASE 
                    WHEN quality_score >= 75 THEN 'excellent'
                    WHEN quality_score >= 50 THEN 'good'
                    ELSE 'poor'
                END as score_category,
                COUNT(*) as count
            FROM project_statuses
            GROUP BY score_category
        """)
        score_results = await cur.fetchall()
        projects_by_score = {row["score_category"]: row["count"] for row in score_results}
        
        return {
            "total_projects": total_projects,
            "projects_with_readme": projects_with_readme,
            "readme_coverage": readme_coverage,
            "avg_quality_score": round(avg_quality_score, 1),
            "language_distribution": language_distribution,
            "avg_project_size": round(avg_project_size, 1),
            "avg_commit_count": round(avg_commit_count, 1),
            "avg_contributors": round(avg_contributors, 1),
            "projects_by_score": projects_by_score
        }


@router.post("/analyze")
async def analyze_projects():
    """手动触发项目分析 - Issue 6: 已移除，请使用独立脚本"""
    raise HTTPException(
        status_code=400, 
        detail="此功能已移除。请使用独立脚本: python scripts/analyze_projects.py"
    )


@router.post("/update-repos")
async def update_local_repos():
    """手动更新本地仓库 - Issue 6: 已移除，请使用独立脚本"""
    raise HTTPException(
        status_code=400, 
        detail="此功能已移除。请使用独立脚本: python scripts/update_repos.py"
    )


@router.post("/sync")
async def manual_sync():
    """手动执行完整同步 - Issue 6: 已移除，请使用独立脚本"""
    raise HTTPException(
        status_code=400, 
        detail="此功能已移除。请使用独立脚本: python scripts/sync_data.py"
    )


@router.post("/analysis-only")
async def analysis_only():
    """仅执行项目分析 - Issue 6: 已移除，请使用独立脚本"""
    raise HTTPException(
        status_code=400, 
        detail="此功能已移除。请使用独立脚本: python scripts/analyze_projects.py"
    )


@router.get("/scheduler/status")
async def get_scheduler_status():
    """获取调度器状态 - Issue 6: 已移除"""
    raise HTTPException(
        status_code=400, 
        detail="调度器已移除。请使用独立脚本查看状态: python scripts/cli.py status"
    ) 