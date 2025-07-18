from fastapi import APIRouter, Depends
from typing import List
import psycopg

from app.database import get_db
from app.models import AnalyticsData


router = APIRouter()


@router.get("/dashboard", response_model=AnalyticsData)
async def get_dashboard_data(db: psycopg.AsyncConnection = Depends(get_db)):
    """获取仪表板数据"""
    async with db.cursor() as cur:
        # 获取基础统计数据
        await cur.execute("SELECT COUNT(*) as count FROM projects")
        total_projects = (await cur.fetchone())["count"]
        
        await cur.execute("SELECT COUNT(*) as count FROM students")
        total_students = (await cur.fetchone())["count"]
        
        await cur.execute("SELECT COUNT(*) as count FROM commits")
        total_commits = (await cur.fetchone())["count"]
        
        await cur.execute("SELECT COUNT(*) as count FROM issues")
        total_issues = (await cur.fetchone())["count"]
        
        # 获取按学生分组的提交数据
        await cur.execute("""
            SELECT s.name, s.github_username, COUNT(c.id) as commit_count
            FROM students s
            LEFT JOIN commits c ON s.id = c.student_id
            GROUP BY s.id, s.name, s.github_username
            ORDER BY commit_count DESC
        """)
        commits_by_student = await cur.fetchall()
        
        # 获取按学生分组的Issue数据
        await cur.execute("""
            SELECT s.name, s.github_username, COUNT(i.id) as issue_count
            FROM students s
            LEFT JOIN issues i ON s.id = i.student_id
            GROUP BY s.id, s.name, s.github_username
            ORDER BY issue_count DESC
        """)
        issues_by_student = await cur.fetchall()
        
        # 获取最近活动
        await cur.execute("""
            SELECT 
                'commit' as type,
                c.commit_message as title,
                s.name as student_name,
                c.commit_date as date
            FROM commits c
            JOIN students s ON c.student_id = s.id
            UNION ALL
            SELECT 
                'issue' as type,
                i.title,
                s.name as student_name,
                i.created_at as date
            FROM issues i
            JOIN students s ON i.student_id = s.id
            ORDER BY date DESC
            LIMIT 20
        """)
        recent_activity = await cur.fetchall()
        
        return AnalyticsData(
            total_projects=total_projects,
            total_students=total_students,
            total_commits=total_commits,
            total_issues=total_issues,
            commits_by_student=commits_by_student,
            issues_by_student=issues_by_student,
            recent_activity=recent_activity
        )


@router.get("/project/{project_id}/stats")
async def get_project_stats(project_id: int, db: psycopg.AsyncConnection = Depends(get_db)):
    """获取指定项目的统计数据"""
    async with db.cursor() as cur:
        # 项目基本信息
        await cur.execute("SELECT * FROM projects WHERE id = %s", (project_id,))
        project = await cur.fetchone()
        if not project:
            return {"error": "项目不存在"}
        
        # 项目统计数据
        await cur.execute("""
            SELECT 
                COUNT(DISTINCT s.id) as student_count,
                COUNT(c.id) as commit_count,
                COUNT(i.id) as issue_count,
                SUM(c.lines_added) as total_lines_added,
                SUM(c.lines_deleted) as total_lines_deleted
            FROM projects p
            LEFT JOIN students s ON p.id = s.project_id
            LEFT JOIN commits c ON s.id = c.student_id
            LEFT JOIN issues i ON s.id = i.student_id
            WHERE p.id = %s
        """, (project_id,))
        stats = await cur.fetchone()
        
        # 学生贡献排名
        await cur.execute("""
            SELECT 
                s.name,
                s.github_username,
                COUNT(c.id) as commit_count,
                COUNT(i.id) as issue_count,
                SUM(COALESCE(c.lines_added, 0)) as lines_added,
                SUM(COALESCE(c.lines_deleted, 0)) as lines_deleted
            FROM students s
            LEFT JOIN commits c ON s.id = c.student_id
            LEFT JOIN issues i ON s.id = i.student_id
            WHERE s.project_id = %s
            GROUP BY s.id, s.name, s.github_username
            ORDER BY commit_count DESC, lines_added DESC
        """, (project_id,))
        student_contributions = await cur.fetchall()
        
        return {
            "project": project,
            "stats": stats,
            "student_contributions": student_contributions
        }


@router.get("/student/{student_id}/stats")
async def get_student_stats(student_id: int, db: psycopg.AsyncConnection = Depends(get_db)):
    """获取指定学生的统计数据"""
    async with db.cursor() as cur:
        # 学生基本信息
        await cur.execute("SELECT * FROM students WHERE id = %s", (student_id,))
        student = await cur.fetchone()
        if not student:
            return {"error": "学生不存在"}
        
        # 学生统计数据
        await cur.execute("""
            SELECT 
                COUNT(c.id) as commit_count,
                COUNT(i.id) as issue_count,
                SUM(COALESCE(c.lines_added, 0)) as total_lines_added,
                SUM(COALESCE(c.lines_deleted, 0)) as total_lines_deleted,
                AVG(COALESCE(c.files_changed, 0)) as avg_files_changed
            FROM students s
            LEFT JOIN commits c ON s.id = c.student_id
            LEFT JOIN issues i ON s.id = i.student_id
            WHERE s.id = %s
        """, (student_id,))
        stats = await cur.fetchone()
        
        # 最近的提交
        await cur.execute("""
            SELECT * FROM commits 
            WHERE student_id = %s 
            ORDER BY commit_date DESC 
            LIMIT 10
        """, (student_id,))
        recent_commits = await cur.fetchall()
        
        # 最近的Issue
        await cur.execute("""
            SELECT * FROM issues 
            WHERE student_id = %s 
            ORDER BY created_at DESC 
            LIMIT 10
        """, (student_id,))
        recent_issues = await cur.fetchall()
        
        return {
            "student": student,
            "stats": stats,
            "recent_commits": recent_commits,
            "recent_issues": recent_issues
        } 