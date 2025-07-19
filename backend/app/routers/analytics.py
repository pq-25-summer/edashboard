"""
分析API路由
提供项目语言和框架统计功能
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, List, Any
import asyncio
from datetime import datetime, timedelta

from app.project_analyzer import ProjectAnalyzer
from app.database import db

router = APIRouter(tags=["analytics"])


@router.get("/dashboard")
async def get_dashboard_data():
    """获取仪表板数据 - 包括项目统计、学生统计、提交统计、Issue统计和最近活动"""
    try:
        # Issue 6: 从数据库读取数据，不执行实时分析
        # 项目分析数据应该通过独立脚本预先计算并存储到数据库
        
        # 从数据库获取学生和项目信息
        async with db.get_db() as conn:
            async with conn.cursor() as cur:
                # 获取项目统计
                await cur.execute("SELECT COUNT(*) FROM projects")
                project_count = (await cur.fetchone())["count"]
                
                # 获取学生统计
                await cur.execute("SELECT COUNT(*) FROM students")
                student_count = (await cur.fetchone())["count"]
                
                # 获取提交统计
                await cur.execute("""
                    SELECT s.name, s.github_username, COUNT(c.id) as commit_count
                    FROM students s
                    LEFT JOIN commits c ON s.id = c.student_id
                    GROUP BY s.id, s.name, s.github_username
                    ORDER BY commit_count DESC
                """)
                commit_data = await cur.fetchall()
                
                # 获取Issue统计
                await cur.execute("""
                    SELECT s.name, s.github_username, COUNT(i.id) as issue_count
                    FROM students s
                    LEFT JOIN issues i ON s.id = i.student_id
                    GROUP BY s.id, s.name, s.github_username
                    ORDER BY issue_count DESC
                """)
                issue_data = await cur.fetchall()
                
                # 获取最近活动（提交和Issue）
                await cur.execute("""
                    SELECT 
                        'commit' as type,
                        c.commit_message as title,
                        s.name as student_name,
                        c.commit_date as date
                    FROM commits c
                    JOIN students s ON c.student_id = s.id
                    WHERE c.commit_date >= %s
                    
                    UNION ALL
                    
                    SELECT 
                        'issue' as type,
                        i.title,
                        s.name as student_name,
                        i.created_at as date
                    FROM issues i
                    JOIN students s ON i.student_id = s.id
                    WHERE i.created_at >= %s
                    
                    ORDER BY date DESC
                    LIMIT 20
                """, (datetime.now() - timedelta(days=30), datetime.now() - timedelta(days=30)))
                recent_activity = await cur.fetchall()
        
        # 计算总提交数和总Issue数
        total_commits = sum(item['commit_count'] for item in commit_data)
        total_issues = sum(item['issue_count'] for item in issue_data)
        
        # 格式化最近活动数据
        formatted_activity = []
        for activity in recent_activity:
            formatted_activity.append({
                'type': activity['type'],
                'title': activity['title'],
                'student_name': activity['student_name'],
                'date': activity['date'].isoformat() if activity['date'] else None
            })
        
        return {
            "total_projects": project_count or 0,
            "total_students": student_count or 0,
            "total_commits": total_commits,
            "total_issues": total_issues,
            "commits_by_student": [
                {
                    "name": item['name'],
                    "github_username": item['github_username'],
                    "commit_count": item['commit_count']
                }
                for item in commit_data
            ],
            "issues_by_student": [
                {
                    "name": item['name'],
                    "github_username": item['github_username'],
                    "issue_count": item['issue_count']
                }
                for item in issue_data
            ],
            "recent_activity": formatted_activity,
            "analysis_time": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取仪表板数据失败: {str(e)}")


@router.get("/languages")
async def get_language_statistics():
    """获取所有项目的编程语言统计"""
    try:
        # Issue 6: 从数据库读取预计算的语言统计，不执行实时分析
        # 语言分析数据应该通过独立脚本预先计算并存储到数据库
        
        # 临时返回空数据，提示用户运行分析脚本
        return {
            "total_projects": 0,
            "language_statistics": {},
            "project_languages": {},
            "analysis_time": datetime.now().isoformat(),
            "message": "请运行 'python scripts/analyze_projects.py' 来生成语言统计数据"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取语言统计失败: {str(e)}")


@router.get("/frameworks")
async def get_framework_statistics():
    """获取所有项目的框架统计"""
    try:
        # Issue 6: 从数据库读取预计算的框架统计，不执行实时分析
        # 框架分析数据应该通过独立脚本预先计算并存储到数据库
        
        # 临时返回空数据，提示用户运行分析脚本
        return {
            "total_projects": 0,
            "framework_statistics": {},
            "project_frameworks": {},
            "analysis_time": datetime.now().isoformat(),
            "message": "请运行 'python scripts/analyze_projects.py' 来生成框架统计数据"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取框架统计失败: {str(e)}")


@router.get("/ai-technologies")
async def get_ai_technology_statistics():
    """获取所有项目的AI技术统计"""
    try:
        # Issue 6: 从数据库读取预计算的AI技术统计，不执行实时分析
        # AI技术分析数据应该通过独立脚本预先计算并存储到数据库
        
        # 临时返回空数据，提示用户运行分析脚本
        return {
            "total_projects": 0,
            "ai_statistics": {
                'models': {},
                'libraries': {},
                'runtimes': {},
                'projects_with_ai': 0,
                'ai_projects': []
            },
            "analysis_time": datetime.now().isoformat(),
            "message": "请运行 'python scripts/analyze_projects.py' 来生成AI技术统计数据"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取AI技术统计失败: {str(e)}")


@router.get("/tech-stack-summary")
async def get_tech_stack_summary():
    """获取技术栈总体摘要"""
    try:
        async with db.get_db() as conn:
            async with conn.cursor() as cur:
                # 获取最新的技术栈统计数据
                await cur.execute("""
                    SELECT language_summary, framework_summary, ai_summary, total_projects, analysis_time
                    FROM tech_stack_statistics
                    ORDER BY analysis_time DESC
                    LIMIT 1
                """)
                result = await cur.fetchone()
                
                if result:
                    # JSONB数据已经自动解析为dict
                    language_summary = result['language_summary'] if result['language_summary'] else {}
                    framework_summary = result['framework_summary'] if result['framework_summary'] else {}
                    ai_summary = result['ai_summary'] if result['ai_summary'] else {}
                    
                    # 获取项目详情
                    await cur.execute("""
                        SELECT p.name, pts.languages, pts.frameworks, pts.ai_models, pts.ai_libraries, pts.has_ai
                        FROM project_tech_stacks pts
                        JOIN projects p ON pts.project_id = p.id
                        ORDER BY p.name
                    """)
                    project_details = await cur.fetchall()
                    
                    # 格式化项目详情
                    formatted_projects = {}
                    for project in project_details:
                        languages = project['languages'] if project['languages'] else {}
                        frameworks = project['frameworks'] if project['frameworks'] else {}
                        ai_models = project['ai_models'] if project['ai_models'] else []
                        ai_libraries = project['ai_libraries'] if project['ai_libraries'] else []
                        has_ai = project['has_ai']
                        
                        # 计算主要语言（文件数最多的）
                        primary_language = max(languages.items(), key=lambda x: x[1])[0] if languages else "未知"
                        language_count = len(languages)
                        framework_count = len(frameworks)
                        
                        # 获取主要框架（使用最多的前3个）
                        main_frameworks = sorted(frameworks.items(), key=lambda x: x[1], reverse=True)[:3]
                        main_frameworks = [fw[0] for fw in main_frameworks]
                        
                        formatted_projects[project['name']] = {
                            'primary_language': primary_language,
                            'language_count': language_count,
                            'framework_count': framework_count,
                            'main_frameworks': main_frameworks,
                            'has_ai': has_ai,
                            'ai_models': ai_models,
                            'ai_libraries': ai_libraries
                        }
                    
                    return {
                        "summary": {
                            "total_projects": result['total_projects'],
                            "language_summary": language_summary,
                            "framework_summary": framework_summary,
                            "ai_summary": ai_summary,
                            "project_details": formatted_projects
                        },
                        "analysis_time": result['analysis_time'].isoformat(),
                        "message": "技术栈数据已成功加载"
                    }
                else:
                    return {
                        "summary": {
                            "total_projects": 0,
                            "language_summary": {},
                            "framework_summary": {},
                            "ai_summary": {
                                'projects_with_ai': 0,
                                'ai_models': {},
                                'ai_libraries': {}
                            },
                            "project_details": {}
                        },
                        "analysis_time": datetime.now().isoformat(),
                        "message": "请运行 'python scripts/cli.py tech-stack' 来生成技术栈摘要数据"
                    }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取技术栈摘要失败: {str(e)}")


@router.get("/project/{project_id}/tech-stack")
async def get_project_tech_stack(project_id: str):
    """获取特定项目的技术栈详情"""
    try:
        # Issue 6: 从数据库读取预计算的项目技术栈，不执行实时分析
        # 项目技术栈数据应该通过独立脚本预先计算并存储到数据库
        
        # 临时返回空数据，提示用户运行分析脚本
        return {
            "project_id": project_id,
            "tech_stack": {},
            "analysis_time": datetime.now().isoformat(),
            "message": "请运行 'python scripts/analyze_projects.py' 来生成项目技术栈数据"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取项目技术栈失败: {str(e)}") 