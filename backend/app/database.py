import psycopg
from psycopg.rows import dict_row
from contextlib import asynccontextmanager
from typing import AsyncGenerator
import asyncio

from app.config import settings


class Database:
    def __init__(self):
        self.connection_string = settings.database_url
    
    async def get_connection(self):
        return await psycopg.AsyncConnection.connect(
            self.connection_string,
            row_factory=dict_row
        )
    
    @asynccontextmanager
    async def get_db(self) -> AsyncGenerator[psycopg.AsyncConnection, None]:
        conn = await self.get_connection()
        try:
            yield conn
        finally:
            await conn.close()


db = Database()


async def init_db():
    """初始化数据库表结构"""
    async with db.get_db() as conn:
        # 创建项目表
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                github_url VARCHAR(500) NOT NULL UNIQUE,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 创建学生表
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                github_username VARCHAR(100) UNIQUE,
                email VARCHAR(255),
                project_id INTEGER REFERENCES projects(id),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 创建提交记录表
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS commits (
                id SERIAL PRIMARY KEY,
                project_id INTEGER REFERENCES projects(id),
                student_id INTEGER REFERENCES students(id),
                commit_hash VARCHAR(40) NOT NULL,
                commit_message TEXT,
                commit_date TIMESTAMP,
                files_changed INTEGER,
                lines_added INTEGER,
                lines_deleted INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 创建Issue表
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS issues (
                id SERIAL PRIMARY KEY,
                project_id INTEGER REFERENCES projects(id),
                student_id INTEGER REFERENCES students(id),
                issue_number INTEGER NOT NULL,
                title VARCHAR(500) NOT NULL,
                body TEXT,
                state VARCHAR(20) NOT NULL,
                created_at TIMESTAMP,
                closed_at TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        await conn.commit()


async def get_db() -> AsyncGenerator[psycopg.AsyncConnection, None]:
    """获取数据库连接的依赖函数"""
    async with db.get_db() as conn:
        yield conn 