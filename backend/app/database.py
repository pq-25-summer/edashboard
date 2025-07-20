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
        
        # 创建项目状态表
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS project_statuses (
                id SERIAL PRIMARY KEY,
                project_id INTEGER REFERENCES projects(id) UNIQUE,
                has_readme BOOLEAN DEFAULT FALSE,
                readme_files TEXT[],
                total_files INTEGER DEFAULT 0,
                code_files INTEGER DEFAULT 0,
                doc_files INTEGER DEFAULT 0,
                config_files INTEGER DEFAULT 0,
                project_size_kb DECIMAL(10,2) DEFAULT 0,
                main_language VARCHAR(50),
                commit_count INTEGER DEFAULT 0,
                contributors INTEGER DEFAULT 0,
                last_commit TEXT,
                current_branch VARCHAR(100) DEFAULT 'main',
                has_package_json BOOLEAN DEFAULT FALSE,
                has_requirements_txt BOOLEAN DEFAULT FALSE,
                has_dockerfile BOOLEAN DEFAULT FALSE,
                quality_score INTEGER DEFAULT 0,
                -- Git工作流程相关字段
                workflow_style VARCHAR(50),
                workflow_score DECIMAL(5,2) DEFAULT 0.0,
                total_branches INTEGER DEFAULT 0,
                feature_branches INTEGER DEFAULT 0,
                hotfix_branches INTEGER DEFAULT 0,
                merge_commits INTEGER DEFAULT 0,
                rebase_commits INTEGER DEFAULT 0,
                uses_feature_branches BOOLEAN DEFAULT FALSE,
                uses_main_branch_merges BOOLEAN DEFAULT FALSE,
                uses_rebase BOOLEAN DEFAULT FALSE,
                uses_pull_requests BOOLEAN DEFAULT FALSE,
                -- Issue驱动开发相关字段
                total_issues INTEGER DEFAULT 0,
                commits_with_issue_refs INTEGER DEFAULT 0,
                commits_without_issue_refs INTEGER DEFAULT 0,
                issues_with_assignees INTEGER DEFAULT 0,
                issues_without_assignees INTEGER DEFAULT 0,
                closed_issues INTEGER DEFAULT 0,
                open_issues INTEGER DEFAULT 0,
                commit_issue_ratio DECIMAL(5,2) DEFAULT 0.0,
                issue_assignee_ratio DECIMAL(5,2) DEFAULT 0.0,
                issue_closure_ratio DECIMAL(5,2) DEFAULT 0.0,
                uses_issue_driven_development BOOLEAN DEFAULT FALSE,
                issue_driven_score DECIMAL(5,2) DEFAULT 0.0,
                issue_workflow_quality VARCHAR(20) DEFAULT '一般',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 添加Git工作流程字段（如果不存在）
        try:
            await conn.execute("""
                ALTER TABLE project_statuses 
                ADD COLUMN IF NOT EXISTS workflow_style VARCHAR(50)
            """)
            await conn.execute("""
                ALTER TABLE project_statuses 
                ADD COLUMN IF NOT EXISTS workflow_score DECIMAL(5,2) DEFAULT 0.0
            """)
            await conn.execute("""
                ALTER TABLE project_statuses 
                ADD COLUMN IF NOT EXISTS total_branches INTEGER DEFAULT 0
            """)
            await conn.execute("""
                ALTER TABLE project_statuses 
                ADD COLUMN IF NOT EXISTS feature_branches INTEGER DEFAULT 0
            """)
            await conn.execute("""
                ALTER TABLE project_statuses 
                ADD COLUMN IF NOT EXISTS hotfix_branches INTEGER DEFAULT 0
            """)
            await conn.execute("""
                ALTER TABLE project_statuses 
                ADD COLUMN IF NOT EXISTS merge_commits INTEGER DEFAULT 0
            """)
            await conn.execute("""
                ALTER TABLE project_statuses 
                ADD COLUMN IF NOT EXISTS rebase_commits INTEGER DEFAULT 0
            """)
            await conn.execute("""
                ALTER TABLE project_statuses 
                ADD COLUMN IF NOT EXISTS uses_feature_branches BOOLEAN DEFAULT FALSE
            """)
            await conn.execute("""
                ALTER TABLE project_statuses 
                ADD COLUMN IF NOT EXISTS uses_main_branch_merges BOOLEAN DEFAULT FALSE
            """)
            await conn.execute("""
                ALTER TABLE project_statuses 
                ADD COLUMN IF NOT EXISTS uses_rebase BOOLEAN DEFAULT FALSE
            """)
            await conn.execute("""
                ALTER TABLE project_statuses 
                ADD COLUMN IF NOT EXISTS uses_pull_requests BOOLEAN DEFAULT FALSE
            """)
        except Exception as e:
            print(f"添加Git工作流程字段时出错（可能已存在）: {e}")
        
        # 添加Issue驱动开发字段（如果不存在）
        try:
            await conn.execute("""
                ALTER TABLE project_statuses 
                ADD COLUMN IF NOT EXISTS total_issues INTEGER DEFAULT 0
            """)
            await conn.execute("""
                ALTER TABLE project_statuses 
                ADD COLUMN IF NOT EXISTS commits_with_issue_refs INTEGER DEFAULT 0
            """)
            await conn.execute("""
                ALTER TABLE project_statuses 
                ADD COLUMN IF NOT EXISTS commits_without_issue_refs INTEGER DEFAULT 0
            """)
            await conn.execute("""
                ALTER TABLE project_statuses 
                ADD COLUMN IF NOT EXISTS issues_with_assignees INTEGER DEFAULT 0
            """)
            await conn.execute("""
                ALTER TABLE project_statuses 
                ADD COLUMN IF NOT EXISTS issues_without_assignees INTEGER DEFAULT 0
            """)
            await conn.execute("""
                ALTER TABLE project_statuses 
                ADD COLUMN IF NOT EXISTS closed_issues INTEGER DEFAULT 0
            """)
            await conn.execute("""
                ALTER TABLE project_statuses 
                ADD COLUMN IF NOT EXISTS open_issues INTEGER DEFAULT 0
            """)
            await conn.execute("""
                ALTER TABLE project_statuses 
                ADD COLUMN IF NOT EXISTS commit_issue_ratio DECIMAL(5,2) DEFAULT 0.0
            """)
            await conn.execute("""
                ALTER TABLE project_statuses 
                ADD COLUMN IF NOT EXISTS issue_assignee_ratio DECIMAL(5,2) DEFAULT 0.0
            """)
            await conn.execute("""
                ALTER TABLE project_statuses 
                ADD COLUMN IF NOT EXISTS issue_closure_ratio DECIMAL(5,2) DEFAULT 0.0
            """)
            await conn.execute("""
                ALTER TABLE project_statuses 
                ADD COLUMN IF NOT EXISTS uses_issue_driven_development BOOLEAN DEFAULT FALSE
            """)
            await conn.execute("""
                ALTER TABLE project_statuses 
                ADD COLUMN IF NOT EXISTS issue_driven_score DECIMAL(5,2) DEFAULT 0.0
            """)
            await conn.execute("""
                ALTER TABLE project_statuses 
                ADD COLUMN IF NOT EXISTS issue_workflow_quality VARCHAR(20) DEFAULT '一般'
            """)
        except Exception as e:
            print(f"添加Issue驱动开发字段时出错（可能已存在）: {e}")
        
        # 创建项目进度跟踪表
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS project_progress (
                id SERIAL PRIMARY KEY,
                project_id INTEGER REFERENCES projects(id),
                date DATE NOT NULL,
                has_commit BOOLEAN DEFAULT FALSE,
                commit_count INTEGER DEFAULT 0,
                lines_added INTEGER DEFAULT 0,
                lines_deleted INTEGER DEFAULT 0,
                files_changed INTEGER DEFAULT 0,
                issues_created INTEGER DEFAULT 0,
                issues_closed INTEGER DEFAULT 0,
                issues_commented INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(project_id, date)
            )
        """)
        
        # 创建索引以提高查询性能
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_project_progress_project_date 
            ON project_progress(project_id, date)
        """)
        
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_project_progress_date 
            ON project_progress(date)
        """)
        
        await conn.commit()


async def get_db() -> AsyncGenerator[psycopg.AsyncConnection, None]:
    """获取数据库连接的依赖函数"""
    async with db.get_db() as conn:
        yield conn 