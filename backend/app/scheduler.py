"""
定时任务调度器
用于定期执行项目状态同步和分析
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional

from app.github_sync import GitHubSync
from app.project_analyzer import ProjectAnalyzer


class Scheduler:
    def __init__(self):
        self.setup_logging()
        self.github_sync = GitHubSync()
        self.project_analyzer = ProjectAnalyzer()
        self.is_running = False
        self.last_sync_time: Optional[datetime] = None
    
    def setup_logging(self):
        """设置日志"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('scheduler.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    async def start_scheduler(self, sync_interval_hours: int = 6):
        """启动定时任务调度器"""
        self.is_running = True
        self.logger.info(f"定时任务调度器已启动，同步间隔: {sync_interval_hours} 小时")
        
        # 延迟30秒后执行第一次同步，避免阻塞服务启动
        await asyncio.sleep(30)
        
        while self.is_running:
            try:
                # 执行同步任务
                await self.run_sync_task()
                
                # 等待下次执行
                await asyncio.sleep(sync_interval_hours * 3600)
                
            except Exception as e:
                self.logger.error(f"定时任务执行失败: {e}")
                # 出错后等待1小时再重试
                await asyncio.sleep(3600)
    
    async def run_sync_task(self):
        """执行同步任务"""
        self.logger.info("开始执行定时同步任务...")
        start_time = datetime.now()
        
        try:
            # 执行GitHub数据同步（包括项目状态分析）
            await self.github_sync.sync_all_projects()
            
            self.last_sync_time = datetime.now()
            duration = self.last_sync_time - start_time
            
            self.logger.info(f"定时同步任务完成，耗时: {duration}")
            
        except Exception as e:
            self.logger.error(f"同步任务执行失败: {e}")
            raise
    
    async def stop_scheduler(self):
        """停止定时任务调度器"""
        self.is_running = False
        self.logger.info("定时任务调度器已停止")
    
    async def run_manual_sync(self):
        """手动执行同步任务"""
        self.logger.info("开始执行手动同步任务...")
        await self.run_sync_task()
        return {
            "status": "success",
            "message": "手动同步任务完成",
            "last_sync_time": self.last_sync_time.isoformat() if self.last_sync_time else None
        }
    
    async def run_analysis_only(self):
        """仅执行项目分析（不更新仓库）"""
        self.logger.info("开始执行项目分析...")
        start_time = datetime.now()
        
        try:
            # 分析项目状态
            results = await self.project_analyzer.analyze_all_projects()
            
            # 保存到数据库
            from app.database import db
            async with db.get_db() as conn:
                await self.github_sync.save_project_statuses(results, conn)
            
            duration = datetime.now() - start_time
            self.logger.info(f"项目分析完成，分析了 {len(results)} 个项目，耗时: {duration}")
            
            return {
                "status": "success",
                "message": "项目分析完成",
                "analyzed_projects": len(results),
                "duration": str(duration)
            }
            
        except Exception as e:
            self.logger.error(f"项目分析失败: {e}")
            raise
    
    def get_status(self):
        """获取调度器状态"""
        return {
            "is_running": self.is_running,
            "last_sync_time": self.last_sync_time.isoformat() if self.last_sync_time else None,
            "uptime": str(datetime.now() - self.last_sync_time) if self.last_sync_time else None
        }


# 全局调度器实例
scheduler = Scheduler()


async def start_background_scheduler():
    """启动后台调度器"""
    # 异步启动调度器，不阻塞主线程
    asyncio.create_task(scheduler.start_scheduler())


async def stop_background_scheduler():
    """停止后台调度器"""
    await scheduler.stop_scheduler() 