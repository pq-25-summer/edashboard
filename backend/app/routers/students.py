from fastapi import APIRouter, Depends, HTTPException
from typing import List
import psycopg

from app.database import get_db
from app.models import Student, StudentCreate


router = APIRouter()


@router.get("/", response_model=List[Student])
async def get_students(db: psycopg.AsyncConnection = Depends(get_db)):
    """获取所有学生列表"""
    async with db.cursor() as cur:
        await cur.execute("SELECT * FROM students ORDER BY created_at DESC")
        students = await cur.fetchall()
        return [Student(**student) for student in students]


@router.get("/{student_id}", response_model=Student)
async def get_student(student_id: int, db: psycopg.AsyncConnection = Depends(get_db)):
    """获取单个学生详情"""
    async with db.cursor() as cur:
        await cur.execute("SELECT * FROM students WHERE id = %s", (student_id,))
        student = await cur.fetchone()
        if not student:
            raise HTTPException(status_code=404, detail="学生不存在")
        return Student(**student)


@router.post("/", response_model=Student)
async def create_student(student: StudentCreate, db: psycopg.AsyncConnection = Depends(get_db)):
    """创建新学生"""
    async with db.cursor() as cur:
        await cur.execute(
            "INSERT INTO students (name, github_username, email, project_id) VALUES (%s, %s, %s, %s) RETURNING *",
            (student.name, student.github_username, student.email, student.project_id)
        )
        new_student = await cur.fetchone()
        await db.commit()
        return Student(**new_student)


@router.put("/{student_id}", response_model=Student)
async def update_student(
    student_id: int, 
    student: StudentCreate, 
    db: psycopg.AsyncConnection = Depends(get_db)
):
    """更新学生信息"""
    async with db.cursor() as cur:
        await cur.execute(
            "UPDATE students SET name = %s, github_username = %s, email = %s, project_id = %s, updated_at = CURRENT_TIMESTAMP WHERE id = %s RETURNING *",
            (student.name, student.github_username, student.email, student.project_id, student_id)
        )
        updated_student = await cur.fetchone()
        if not updated_student:
            raise HTTPException(status_code=404, detail="学生不存在")
        await db.commit()
        return Student(**updated_student)


@router.delete("/{student_id}")
async def delete_student(student_id: int, db: psycopg.AsyncConnection = Depends(get_db)):
    """删除学生"""
    async with db.cursor() as cur:
        await cur.execute("DELETE FROM students WHERE id = %s", (student_id,))
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="学生不存在")
        await db.commit()
        return {"message": "学生删除成功"}


@router.get("/project/{project_id}", response_model=List[Student])
async def get_students_by_project(project_id: int, db: psycopg.AsyncConnection = Depends(get_db)):
    """获取指定项目的所有学生"""
    async with db.cursor() as cur:
        await cur.execute("SELECT * FROM students WHERE project_id = %s ORDER BY created_at DESC", (project_id,))
        students = await cur.fetchall()
        return [Student(**student) for student in students] 