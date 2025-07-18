from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # 数据库配置
    database_url: str = "postgresql://localhost/edashboard"
    
    # GitHub API配置
    github_token: Optional[str] = None
    github_api_base_url: str = "https://api.github.com"
    
    # 应用配置
    app_name: str = "软件工程课看板系统"
    debug: bool = True
    
    # 安全配置
    secret_key: str = "your-secret-key-here"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    class Config:
        env_file = ".env"


settings = Settings() 