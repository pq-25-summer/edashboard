"""
GitHub数据同步模块
用于定时同步GitHub项目数据到数据库
"""

import asyncio
import httpx
from datetime import datetime
from typing import List, Dict, Any

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import db
from app.config import settings
from app.project_analyzer import ProjectAnalyzer


class GitHubSync:
    def __init__(self):
        self.base_url = settings.github_api_base_url
        self.headers = {
            "Authorization": f"token {settings.github_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        self.project_analyzer = ProjectAnalyzer()
    
    async def sync_all_projects(self):
        """同步所有项目的数据"""
        # 首先更新本地仓库
        print("正在更新本地仓库...")
        await self.project_analyzer.update_local_repos()
        
        # 分析项目状态
        print("正在分析项目状态...")
        project_statuses = await self.project_analyzer.analyze_all_projects()
        
        # 直接使用数据库实例获取连接
        async with db.get_db() as conn:
            # 获取所有项目
            async with conn.cursor() as cur:
                await cur.execute("SELECT * FROM projects")
                projects = await cur.fetchall()
            
            print(f"找到 {len(projects)} 个项目需要同步")
            
            for project in projects:
                print(f"正在同步项目: {project['name']} ({project['github_url']})")
                await self.sync_project(project, conn)
            
            # 保存项目状态到数据库
            print("正在保存项目状态...")
            await self.save_project_statuses(project_statuses, conn)
    
    async def sync_project(self, project: Dict[str, Any], db):
        """同步单个项目的数据"""
        # 从GitHub URL提取owner和repo
        github_url = project["github_url"]
        owner, repo = self._extract_owner_repo(github_url)
        
        if not owner or not repo:
            print(f"无法解析GitHub URL: {github_url}")
            return
        
        print(f"  解析结果: owner={owner}, repo={repo}")
        
        # 同步提交数据
        await self.sync_commits(owner, repo, project["id"], db)
        
        # 同步Issue数据
        await self.sync_issues(owner, repo, project["id"], db)
    
    async def sync_commits(self, owner: str, repo: str, project_id: int, db):
        """同步提交数据"""
        url = f"{self.base_url}/repos/{owner}/{repo}/commits"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers)
            if response.status_code == 200:
                commits = response.json()
                print(f"    找到 {len(commits)} 个提交")
                
                saved_count = 0
                for commit_data in commits[:100]:  # 限制最近100个提交
                    if await self._save_commit(commit_data, project_id, db):
                        saved_count += 1
                
                print(f"    成功保存 {saved_count} 个提交")
            else:
                print(f"    获取提交失败: {response.status_code} - {response.text}")
    
    async def sync_issues(self, owner: str, repo: str, project_id: int, db):
        """同步Issue数据"""
        url = f"{self.base_url}/repos/{owner}/{repo}/issues"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers)
            if response.status_code == 200:
                issues = response.json()
                
                for issue_data in issues:
                    await self._save_issue(issue_data, project_id, db)
    
    async def _save_commit(self, commit_data: Dict[str, Any], project_id: int, db):
        """保存提交数据到数据库"""
        commit_hash = commit_data["sha"]
        commit_message = commit_data["commit"]["message"]
        commit_date = datetime.fromisoformat(commit_data["commit"]["author"]["date"].replace("Z", "+00:00"))
        author_name = commit_data["commit"]["author"]["name"]
        
        # 查找对应的学生
        student_id = await self._find_student_by_name(author_name, project_id, db)
        
        if student_id:
            async with db.cursor() as cur:
                # 检查是否已存在
                await cur.execute(
                    "SELECT id FROM commits WHERE commit_hash = %s AND project_id = %s",
                    (commit_hash, project_id)
                )
                existing = await cur.fetchone()
                
                if not existing:
                    await cur.execute("""
                        INSERT INTO commits (project_id, student_id, commit_hash, commit_message, commit_date)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (project_id, student_id, commit_hash, commit_message, commit_date))
                    await db.commit()
                    return True
                else:
                    return False
        else:
            print(f"      未找到学生: {author_name} (项目ID: {project_id})")
            return False
    
    async def _save_issue(self, issue_data: Dict[str, Any], project_id: int, db):
        """保存Issue数据到数据库"""
        issue_number = issue_data["number"]
        title = issue_data["title"]
        body = issue_data.get("body", "")
        state = issue_data["state"]
        created_at = datetime.fromisoformat(issue_data["created_at"].replace("Z", "+00:00"))
        closed_at = None
        if issue_data["closed_at"]:
            closed_at = datetime.fromisoformat(issue_data["closed_at"].replace("Z", "+00:00"))
        
        author_name = issue_data["user"]["login"]
        
        # 查找对应的学生
        student_id = await self._find_student_by_github_username(author_name, project_id, db)
        
        if student_id:
            async with db.cursor() as cur:
                # 检查是否已存在
                await cur.execute(
                    "SELECT id FROM issues WHERE issue_number = %s AND project_id = %s",
                    (issue_number, project_id)
                )
                existing = await cur.fetchone()
                
                if not existing:
                    await cur.execute("""
                        INSERT INTO issues (project_id, student_id, issue_number, title, body, state, created_at, closed_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """, (project_id, student_id, issue_number, title, body, state, created_at, closed_at))
                    await db.commit()
    
    async def _find_student_by_name(self, name: str, project_id: int, db) -> int:
        """根据姓名查找学生ID"""
        async with db.cursor() as cur:
            # 首先尝试在指定项目中查找
            await cur.execute(
                "SELECT id FROM students WHERE name = %s AND project_id = %s",
                (name, project_id)
            )
            result = await cur.fetchone()
            if result:
                return result["id"]
            
            # 如果没找到，尝试在所有学生中查找（不限制项目）
            await cur.execute(
                "SELECT id FROM students WHERE name = %s",
                (name,)
            )
            result = await cur.fetchone()
            return result["id"] if result else None
    
    async def _find_student_by_github_username(self, username: str, project_id: int, db) -> int:
        """根据GitHub用户名查找学生ID"""
        async with db.cursor() as cur:
            # 首先尝试在指定项目中查找
            await cur.execute(
                "SELECT id FROM students WHERE github_username = %s AND project_id = %s",
                (username, project_id)
            )
            result = await cur.fetchone()
            if result:
                return result["id"]
            
            # 如果没找到，尝试在所有学生中查找（不限制项目）
            await cur.execute(
                "SELECT id FROM students WHERE github_username = %s",
                (username,)
            )
            result = await cur.fetchone()
            return result["id"] if result else None
    
    async def save_project_statuses(self, project_statuses: Dict[str, Dict], db):
        """保存项目状态到数据库"""
        for project_key, status_data in project_statuses.items():
            # 查找对应的项目ID
            project_id = await self._find_project_by_key(project_key, db)
            if not project_id:
                print(f"未找到项目: {project_key}")
                continue
            
            structure = status_data['structure']
            git_info = status_data['git_info']
            
            async with db.cursor() as cur:
                # 检查是否已存在
                await cur.execute(
                    "SELECT id FROM project_statuses WHERE project_id = %s",
                    (project_id,)
                )
                existing = await cur.fetchone()
                
                status_data_to_save = {
                    'project_id': project_id,
                    'has_readme': structure['has_readme'],
                    'readme_files': structure['readme_files'],
                    'total_files': structure['total_files'],
                    'code_files': structure['code_files'],
                    'doc_files': structure['doc_files'],
                    'config_files': structure['config_files'],
                    'project_size_kb': structure['project_size_kb'],
                    'main_language': structure['main_language'],
                    'commit_count': git_info['commit_count'],
                    'contributors': git_info['contributors'],
                    'last_commit': git_info['last_commit'],
                    'current_branch': git_info['branch'],
                    'has_package_json': structure['has_package_json'],
                    'has_requirements_txt': structure['has_requirements_txt'],
                    'has_dockerfile': structure['has_dockerfile'],
                    'quality_score': status_data['quality_score']
                }
                
                if existing:
                    # 更新现有记录
                    await cur.execute("""
                        UPDATE project_statuses SET
                            has_readme = %(has_readme)s,
                            readme_files = %(readme_files)s,
                            total_files = %(total_files)s,
                            code_files = %(code_files)s,
                            doc_files = %(doc_files)s,
                            config_files = %(config_files)s,
                            project_size_kb = %(project_size_kb)s,
                            main_language = %(main_language)s,
                            commit_count = %(commit_count)s,
                            contributors = %(contributors)s,
                            last_commit = %(last_commit)s,
                            current_branch = %(current_branch)s,
                            has_package_json = %(has_package_json)s,
                            has_requirements_txt = %(has_requirements_txt)s,
                            has_dockerfile = %(has_dockerfile)s,
                            quality_score = %(quality_score)s,
                            updated_at = NOW()
                        WHERE project_id = %(project_id)s
                    """, status_data_to_save)
                else:
                    # 插入新记录
                    await cur.execute("""
                        INSERT INTO project_statuses (
                            project_id, has_readme, readme_files, total_files, code_files,
                            doc_files, config_files, project_size_kb, main_language,
                            commit_count, contributors, last_commit, current_branch,
                            has_package_json, has_requirements_txt, has_dockerfile,
                            quality_score, created_at, updated_at
                        ) VALUES (
                            %(project_id)s, %(has_readme)s, %(readme_files)s, %(total_files)s,
                            %(code_files)s, %(doc_files)s, %(config_files)s, %(project_size_kb)s,
                            %(main_language)s, %(commit_count)s, %(contributors)s, %(last_commit)s,
                            %(current_branch)s, %(has_package_json)s, %(has_requirements_txt)s,
                            %(has_dockerfile)s, %(quality_score)s, NOW(), NOW()
                        )
                    """, status_data_to_save)
                
                await db.commit()
                print(f"已保存项目状态: {project_key}")
    
    async def _find_project_by_key(self, project_key: str, db) -> int:
        """根据项目键查找项目ID"""
        # 从project_key中提取owner和repo
        parts = project_key.split('/')
        if len(parts) >= 2:
            owner, repo = parts[0], parts[1]
            
            async with db.cursor() as cur:
                await cur.execute(
                    "SELECT id FROM projects WHERE github_url LIKE %s",
                    (f"%{owner}/{repo}%",)
                )
                result = await cur.fetchone()
                return result["id"] if result else None
        
        return None
    
    def _extract_owner_repo(self, github_url: str) -> tuple:
        """从GitHub URL提取owner和repo"""
        try:
            # 处理不同格式的GitHub URL
            if github_url.startswith("https://github.com/"):
                parts = github_url.replace("https://github.com/", "").split("/")
                if len(parts) >= 2:
                    return parts[0], parts[1].replace(".git", "")
        except Exception as e:
            print(f"解析GitHub URL失败: {e}")
        return None, None


async def main():
    """主函数"""
    if not settings.github_token:
        print("错误: 未设置GitHub token")
        return
    
    sync = GitHubSync()
    await sync.sync_all_projects()
    print("GitHub数据同步完成")


if __name__ == "__main__":
    asyncio.run(main()) 