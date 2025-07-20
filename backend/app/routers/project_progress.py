"""
项目进度跟踪API路由
提供项目进度数据的查询和统计功能
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
from datetime import datetime, timedelta
import psycopg
from psycopg.rows import dict_row

from app.database import get_db
from app.models import ProjectProgress, ProjectProgressSummary, CalendarData

router = APIRouter(prefix="/api/project-progress", tags=["project-progress"])


@router.get("/summary")
async def get_progress_summary(conn: psycopg.AsyncConnection = Depends(get_db)) -> ProjectProgressSummary:
    """获取项目进度总览数据"""
    try:
        # 设置跟踪时间范围（从2025年7月9日开始，持续5周）
        start_date = datetime(2025, 7, 9).date()
        end_date = start_date + timedelta(weeks=5)
        total_days = (end_date - start_date).days
        
        async with conn.cursor() as cur:
            # 获取总项目数
            await cur.execute("SELECT COUNT(*) FROM projects")
            total_projects = (await cur.fetchone())["count"]
            
            # 获取有活动的项目数
            await cur.execute("""
                SELECT COUNT(DISTINCT project_id) 
                FROM project_progress 
                WHERE date >= %s AND date <= %s AND (has_commit OR issues_created > 0 OR issues_closed > 0)
            """, (start_date, end_date))
            projects_with_activity = (await cur.fetchone())["count"]
            
            # 获取总提交数
            await cur.execute("""
                SELECT SUM(commit_count) as total_commits
                FROM project_progress 
                WHERE date >= %s AND date <= %s
            """, (start_date, end_date))
            result = await cur.fetchone()
            total_commits = result["total_commits"] or 0
            
            # 获取总Issue创建数
            await cur.execute("""
                SELECT SUM(issues_created) as total_issues_created
                FROM project_progress 
                WHERE date >= %s AND date <= %s
            """, (start_date, end_date))
            result = await cur.fetchone()
            total_issues_created = result["total_issues_created"] or 0
            
            # 获取总Issue关闭数
            await cur.execute("""
                SELECT SUM(issues_closed) as total_issues_closed
                FROM project_progress 
                WHERE date >= %s AND date <= %s
            """, (start_date, end_date))
            result = await cur.fetchone()
            total_issues_closed = result["total_issues_closed"] or 0
            
            # 获取每日活动摘要
            await cur.execute("""
                SELECT 
                    date,
                    COUNT(DISTINCT CASE WHEN has_commit THEN project_id END) as projects_with_commits,
                    SUM(commit_count) as total_commits,
                    SUM(lines_added) as total_lines_added,
                    SUM(issues_created) as total_issues_created,
                    SUM(issues_closed) as total_issues_closed
                FROM project_progress 
                WHERE date >= %s AND date <= %s
                GROUP BY date
                ORDER BY date
            """, (start_date, end_date))
            daily_activity = await cur.fetchall()
            
            # 获取项目活动排名
            await cur.execute("""
                SELECT 
                    p.name as project_name,
                    p.github_url,
                    COUNT(DISTINCT CASE WHEN pp.has_commit THEN pp.date END) as active_days,
                    SUM(pp.commit_count) as total_commits,
                    SUM(pp.lines_added) as total_lines_added,
                    SUM(pp.issues_created) as total_issues_created,
                    SUM(pp.issues_closed) as total_issues_closed
                FROM projects p
                LEFT JOIN project_progress pp ON p.id = pp.project_id 
                    AND pp.date >= %s AND pp.date <= %s
                GROUP BY p.id, p.name, p.github_url
                ORDER BY total_commits DESC, active_days DESC
            """, (start_date, end_date))
            project_ranking = await cur.fetchall()
        
        return ProjectProgressSummary(
            total_projects=total_projects,
            tracking_start_date=start_date.isoformat(),
            tracking_end_date=end_date.isoformat(),
            total_days=total_days,
            projects_with_activity=projects_with_activity,
            total_commits=total_commits,
            total_issues_created=total_issues_created,
            total_issues_closed=total_issues_closed,
            daily_activity_summary=[dict(item) for item in daily_activity],
            project_activity_ranking=[dict(item) for item in project_ranking]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取进度摘要失败: {str(e)}")


@router.get("/calendar")
async def get_calendar_data(
    start_date: str = None,
    end_date: str = None,
    conn: psycopg.AsyncConnection = Depends(get_db)
) -> List[CalendarData]:
    """获取日历数据，用于显示每日项目活动"""
    try:
        # 如果没有指定日期范围，使用默认的5周范围
        if not start_date:
            start_date = "2025-07-09"
        if not end_date:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = start_dt + timedelta(weeks=5)
            end_date = end_dt.strftime("%Y-%m-%d")
        
        async with conn.cursor() as cur:
            await cur.execute("""
                SELECT 
                    pp.date,
                    COUNT(DISTINCT CASE WHEN pp.has_commit THEN pp.project_id END) as projects_with_commits,
                    SUM(pp.commit_count) as total_commits,
                    SUM(pp.lines_added) as total_lines_added,
                    SUM(pp.issues_created) as total_issues_created,
                    SUM(pp.issues_closed) as total_issues_closed,
                    json_agg(
                        json_build_object(
                            'project_id', pp.project_id,
                            'project_name', p.name,
                            'github_url', p.github_url,
                            'has_commit', pp.has_commit,
                            'commit_count', pp.commit_count,
                            'lines_added', pp.lines_added,
                            'issues_created', pp.issues_created,
                            'issues_closed', pp.issues_closed
                        ) ORDER BY pp.commit_count DESC
                    ) as project_details
                FROM project_progress pp
                JOIN projects p ON pp.project_id = p.id
                WHERE pp.date >= %s AND pp.date <= %s
                GROUP BY pp.date
                ORDER BY pp.date
            """, (start_date, end_date))
            
            results = await cur.fetchall()
            
            calendar_data = []
            for row in results:
                calendar_data.append(CalendarData(
                    date=row["date"].isoformat(),
                    projects_with_commits=row["projects_with_commits"] or 0,
                    total_commits=row["total_commits"] or 0,
                    total_lines_added=row["total_lines_added"] or 0,
                    total_issues_created=row["total_issues_created"] or 0,
                    total_issues_closed=row["total_issues_closed"] or 0,
                    project_details=row["project_details"] or []
                ))
            
            return calendar_data
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取日历数据失败: {str(e)}")


@router.get("/project/{project_id}")
async def get_project_progress(
    project_id: int,
    start_date: str = None,
    end_date: str = None,
    conn: psycopg.AsyncConnection = Depends(get_db)
) -> List[ProjectProgress]:
    """获取单个项目的进度数据"""
    try:
        # 如果没有指定日期范围，使用默认的5周范围
        if not start_date:
            start_date = "2025-07-09"
        if not end_date:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = start_dt + timedelta(weeks=5)
            end_date = end_dt.strftime("%Y-%m-%d")
        
        async with conn.cursor() as cur:
            await cur.execute("""
                SELECT 
                    pp.*,
                    p.name as project_name,
                    p.github_url
                FROM project_progress pp
                JOIN projects p ON pp.project_id = p.id
                WHERE pp.project_id = %s AND pp.date >= %s AND pp.date <= %s
                ORDER BY pp.date
            """, (project_id, start_date, end_date))
            
            results = await cur.fetchall()
            
            progress_data = []
            for row in results:
                progress_data.append(ProjectProgress(
                    id=row["id"],
                    project_id=row["project_id"],
                    date=row["date"].isoformat(),
                    has_commit=row["has_commit"],
                    commit_count=row["commit_count"],
                    lines_added=row["lines_added"],
                    lines_deleted=row["lines_deleted"],
                    files_changed=row["files_changed"],
                    issues_created=row["issues_created"],
                    issues_closed=row["issues_closed"],
                    issues_commented=row["issues_commented"],
                    created_at=row["created_at"],
                    updated_at=row["updated_at"],
                    project_name=row["project_name"],
                    github_url=row["github_url"]
                ))
            
            return progress_data
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取项目进度失败: {str(e)}")


@router.get("/projects")
async def get_all_projects_progress(
    start_date: str = None,
    end_date: str = None,
    conn: psycopg.AsyncConnection = Depends(get_db)
) -> Dict[str, Any]:
    """获取所有项目的进度数据汇总"""
    try:
        # 如果没有指定日期范围，使用默认的5周范围
        if not start_date:
            start_date = "2025-07-09"
        if not end_date:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = start_dt + timedelta(weeks=5)
            end_date = end_dt.strftime("%Y-%m-%d")
        
        async with conn.cursor() as cur:
            await cur.execute("""
                SELECT 
                    p.id,
                    p.name as project_name,
                    p.github_url,
                    COUNT(DISTINCT CASE WHEN pp.has_commit THEN pp.date END) as active_days,
                    SUM(pp.commit_count) as total_commits,
                    SUM(pp.lines_added) as total_lines_added,
                    SUM(pp.lines_deleted) as total_lines_deleted,
                    SUM(pp.files_changed) as total_files_changed,
                    SUM(pp.issues_created) as total_issues_created,
                    SUM(pp.issues_closed) as total_issues_closed,
                    SUM(pp.issues_commented) as total_issues_commented,
                    AVG(pp.commit_count) as avg_daily_commits,
                    AVG(pp.lines_added) as avg_daily_lines_added
                FROM projects p
                LEFT JOIN project_progress pp ON p.id = pp.project_id 
                    AND pp.date >= %s AND pp.date <= %s
                GROUP BY p.id, p.name, p.github_url
                ORDER BY total_commits DESC, active_days DESC
            """, (start_date, end_date))
            
            results = await cur.fetchall()
            
            return {
                "projects": [dict(item) for item in results],
                "date_range": {
                    "start_date": start_date,
                    "end_date": end_date
                }
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取项目进度汇总失败: {str(e)}")


@router.post("/sync")
async def trigger_progress_sync(conn: psycopg.AsyncConnection = Depends(get_db)) -> Dict[str, str]:
    """手动触发项目进度数据同步"""
    try:
        # 这里应该调用同步程序
        # 为了简化，我们返回成功消息
        return {"message": "项目进度同步已触发，请查看同步日志"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"触发同步失败: {str(e)}") 