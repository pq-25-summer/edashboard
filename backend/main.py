from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

from app.database import init_db
from app.routers import projects, students, analytics, project_status
from app.scheduler import start_background_scheduler, stop_background_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时初始化数据库
    await init_db()
    
    # 启动后台调度器
    import asyncio
    scheduler_task = asyncio.create_task(start_background_scheduler())
    
    yield
    
    # 关闭时的清理工作
    await stop_background_scheduler()
    scheduler_task.cancel()
    try:
        await scheduler_task
    except asyncio.CancelledError:
        pass


app = FastAPI(
    title="软件工程课看板系统",
    description="用于分析和查看学员们学习情况的看板系统",
    version="1.0.0",
    lifespan=lifespan
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Vite默认端口
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(projects.router, prefix="/api/projects", tags=["projects"])
app.include_router(students.router, prefix="/api/students", tags=["students"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])
app.include_router(project_status.router, prefix="/api", tags=["project-status"])


@app.get("/")
async def root():
    return {"message": "软件工程课看板系统API"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 