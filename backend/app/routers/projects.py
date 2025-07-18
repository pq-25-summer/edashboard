from fastapi import APIRouter, Depends, HTTPException
from typing import List
import psycopg

from app.database import get_db
from app.models import Project, ProjectCreate


router = APIRouter()


@router.get("/", response_model=List[Project])
async def get_projects(db: psycopg.AsyncConnection = Depends(get_db)):
    """获取所有项目列表"""
    async with db.cursor() as cur:
        await cur.execute("SELECT * FROM projects ORDER BY created_at DESC")
        projects = await cur.fetchall()
        return [Project(**project) for project in projects]


@router.get("/{project_id}", response_model=Project)
async def get_project(project_id: int, db: psycopg.AsyncConnection = Depends(get_db)):
    """获取单个项目详情"""
    async with db.cursor() as cur:
        await cur.execute("SELECT * FROM projects WHERE id = %s", (project_id,))
        project = await cur.fetchone()
        if not project:
            raise HTTPException(status_code=404, detail="项目不存在")
        return Project(**project)


@router.post("/", response_model=Project)
async def create_project(project: ProjectCreate, db: psycopg.AsyncConnection = Depends(get_db)):
    """创建新项目"""
    async with db.cursor() as cur:
        await cur.execute(
            "INSERT INTO projects (name, github_url, description) VALUES (%s, %s, %s) RETURNING *",
            (project.name, str(project.github_url), project.description)
        )
        new_project = await cur.fetchone()
        await db.commit()
        return Project(**new_project)


@router.put("/{project_id}", response_model=Project)
async def update_project(
    project_id: int, 
    project: ProjectCreate, 
    db: psycopg.AsyncConnection = Depends(get_db)
):
    """更新项目信息"""
    async with db.cursor() as cur:
        await cur.execute(
            "UPDATE projects SET name = %s, github_url = %s, description = %s, updated_at = CURRENT_TIMESTAMP WHERE id = %s RETURNING *",
            (project.name, str(project.github_url), project.description, project_id)
        )
        updated_project = await cur.fetchone()
        if not updated_project:
            raise HTTPException(status_code=404, detail="项目不存在")
        await db.commit()
        return Project(**updated_project)


@router.delete("/{project_id}")
async def delete_project(project_id: int, db: psycopg.AsyncConnection = Depends(get_db)):
    """删除项目"""
    async with db.cursor() as cur:
        await cur.execute("DELETE FROM projects WHERE id = %s", (project_id,))
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="项目不存在")
        await db.commit()
        return {"message": "项目删除成功"} 