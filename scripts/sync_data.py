#!/usr/bin/env python3
"""
数据同步脚本
将 scripts/projects.txt 和 scripts/students.txt 中的数据通过API写入数据库
"""

import httpx
import os
import sys
from typing import List, Dict, Optional
from urllib.parse import urlparse
import time


class DataSyncClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0)
        self.projects_cache: Dict[str, int] = {}  # 项目名称 -> 项目ID的缓存
    
    async def close(self):
        """关闭HTTP客户端"""
        await self.client.aclose()
    
    async def test_connection(self) -> bool:
        """测试API连接"""
        try:
            response = await self.client.get(f"{self.base_url}/")
            return response.status_code == 200
        except Exception as e:
            print(f"连接测试失败: {e}")
            return False
    
    async def create_project(self, name: str, github_url: str, description: str = None) -> Optional[int]:
        """创建项目"""
        try:
            data = {
                "name": name,
                "github_url": github_url,
                "description": description
            }
            
            response = await self.client.post(
                f"{self.base_url}/api/projects/",
                json=data
            )
            
            if response.status_code in [200, 201]:
                project_data = response.json()
                project_id = project_data.get("id")
                print(f"✅ 创建项目成功: {name} (ID: {project_id})")
                return project_id
            else:
                print(f"❌ 创建项目失败: {name} - {response.status_code}: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ 创建项目异常: {name} - {e}")
            return None
    
    async def create_student(self, name: str, github_username: str, github_url: str, project_id: int = None) -> Optional[int]:
        """创建学生"""
        try:
            data = {
                "name": name,
                "github_username": github_username,
                "email": None,  # 暂时不设置邮箱
                "project_id": project_id
            }
            
            response = await self.client.post(
                f"{self.base_url}/api/students/",
                json=data
            )
            
            if response.status_code in [200, 201]:
                student_data = response.json()
                student_id = student_data.get("id")
                print(f"✅ 创建学生成功: {name} (@{github_username}) (ID: {student_id})")
                return student_id
            else:
                print(f"❌ 创建学生失败: {name} - {response.status_code}: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ 创建学生异常: {name} - {e}")
            return None
    
    async def get_existing_projects(self) -> Dict[str, int]:
        """获取现有项目列表"""
        try:
            response = await self.client.get(f"{self.base_url}/api/projects/")
            if response.status_code == 200:
                projects = response.json()
                return {project["name"]: project["id"] for project in projects}
            else:
                print(f"❌ 获取项目列表失败: {response.status_code}")
                return {}
        except Exception as e:
            print(f"❌ 获取项目列表异常: {e}")
            return {}
    
    async def get_existing_students(self) -> Dict[str, int]:
        """获取现有学生列表"""
        try:
            response = await self.client.get(f"{self.base_url}/api/students/")
            if response.status_code == 200:
                students = response.json()
                return {student["name"]: student["id"] for student in students}
            else:
                print(f"❌ 获取学生列表失败: {response.status_code}")
                return {}
        except Exception as e:
            print(f"❌ 获取学生列表异常: {e}")
            return {}
    
    def parse_projects_file(self, file_path: str) -> List[Dict[str, str]]:
        """解析项目文件"""
        projects = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue
                    
                    parts = line.split('\t')
                    if len(parts) >= 2:
                        name = parts[0].strip()
                        github_url = parts[1].strip()
                        
                        # 验证GitHub URL格式
                        if not github_url.startswith('https://github.com/'):
                            print(f"⚠️  警告: 第{line_num}行的GitHub URL格式可能不正确: {github_url}")
                        
                        projects.append({
                            "name": name,
                            "github_url": github_url
                        })
                    else:
                        print(f"⚠️  警告: 第{line_num}行格式不正确: {line}")
            
            print(f"📖 从 {file_path} 读取到 {len(projects)} 个项目")
            return projects
            
        except FileNotFoundError:
            print(f"❌ 文件不存在: {file_path}")
            return []
        except Exception as e:
            print(f"❌ 读取项目文件失败: {e}")
            return []
    
    def parse_students_file(self, file_path: str) -> List[Dict[str, str]]:
        """解析学生文件"""
        students = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue
                    
                    parts = line.split('\t')
                    if len(parts) >= 3:
                        name = parts[0].strip()
                        github_username = parts[1].strip()
                        github_url = parts[2].strip()
                        
                        students.append({
                            "name": name,
                            "github_username": github_username,
                            "github_url": github_url
                        })
                    else:
                        print(f"⚠️  警告: 第{line_num}行格式不正确: {line}")
            
            print(f"📖 从 {file_path} 读取到 {len(students)} 个学生")
            return students
            
        except FileNotFoundError:
            print(f"❌ 文件不存在: {file_path}")
            return []
        except Exception as e:
            print(f"❌ 读取学生文件失败: {e}")
            return []
    
    def match_students_to_projects(self, students: List[Dict], projects: List[Dict]) -> List[Dict]:
        """将学生匹配到项目（基于GitHub URL）"""
        # 由于项目URL和学生URL的格式不同，这里不进行自动匹配
        # 项目URL: https://github.com/组织名/仓库名
        # 学生URL: https://github.com/个人用户名
        # 它们通常不匹配，需要手动关联
        
        for student in students:
            student["matched_project"] = None
        
        return students
    
    async def sync_data(self, projects_file: str, students_file: str, dry_run: bool = False):
        """同步数据到数据库"""
        print("🚀 开始数据同步...")
        
        # 在预览模式下跳过连接测试
        if not dry_run:
            # 测试连接
            if not await self.test_connection():
                print("❌ 无法连接到API服务器，请确保后端服务正在运行")
                return
            print("✅ API连接正常")
        else:
            print("🔍 预览模式 - 跳过API连接测试")
        
        # 读取文件
        projects = self.parse_projects_file(projects_file)
        students = self.parse_students_file(students_file)
        
        if not projects and not students:
            print("❌ 没有找到有效数据，同步终止")
            return
        
        # 匹配学生到项目
        students = self.match_students_to_projects(students, projects)
        
        if dry_run:
            print("\n🔍 预览模式 - 不会实际写入数据库")
            print(f"📊 将创建 {len(projects)} 个项目")
            print(f"👥 将创建 {len(students)} 个学生")
            
            print("\n📋 项目列表:")
            for project in projects:
                print(f"  - {project['name']}: {project['github_url']}")
            
            print("\n👥 学生列表:")
            for student in students:
                project_name = student['matched_project']['name'] if student['matched_project'] else "未匹配"
                print(f"  - {student['name']} (@{student['github_username']}) -> {project_name}")
            
            return
        
        # 获取现有数据
        existing_projects = await self.get_existing_projects()
        existing_students = await self.get_existing_students()
        
        print(f"📊 现有项目: {len(existing_projects)} 个")
        print(f"👥 现有学生: {len(existing_students)} 个")
        
        # 创建项目
        created_projects = 0
        for project in projects:
            if project["name"] in existing_projects:
                print(f"⏭️  项目已存在: {project['name']}")
                self.projects_cache[project["name"]] = existing_projects[project["name"]]
            else:
                project_id = await self.create_project(
                    name=project["name"],
                    github_url=project["github_url"]
                )
                if project_id:
                    self.projects_cache[project["name"]] = project_id
                    created_projects += 1
                    time.sleep(0.1)  # 避免请求过快
        
        # 创建学生
        created_students = 0
        for student in students:
            if student["name"] in existing_students:
                print(f"⏭️  学生已存在: {student['name']}")
                continue
            
            # 确定项目ID
            project_id = None
            if student["matched_project"]:
                project_name = student["matched_project"]["name"]
                project_id = self.projects_cache.get(project_name)
            
            student_id = await self.create_student(
                name=student["name"],
                github_username=student["github_username"],
                github_url=student["github_url"],
                project_id=project_id
            )
            if student_id:
                created_students += 1
                time.sleep(0.1)  # 避免请求过快
        
        print(f"\n✅ 同步完成!")
        print(f"📊 创建项目: {created_projects} 个")
        print(f"👥 创建学生: {created_students} 个")


async def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="数据同步脚本")
    parser.add_argument("--api-url", default="http://localhost:8000", help="API服务器地址")
    parser.add_argument("--projects-file", default="projects.txt", help="项目文件路径")
    parser.add_argument("--students-file", default="students.txt", help="学生文件路径")
    parser.add_argument("--dry-run", action="store_true", help="预览模式，不实际写入数据库")
    
    args = parser.parse_args()
    
    # 检查文件是否存在
    if not os.path.exists(args.projects_file):
        print(f"❌ 项目文件不存在: {args.projects_file}")
        sys.exit(1)
    
    if not os.path.exists(args.students_file):
        print(f"❌ 学生文件不存在: {args.students_file}")
        sys.exit(1)
    
    # 创建同步客户端
    client = DataSyncClient(args.api_url)
    
    try:
        await client.sync_data(
            projects_file=args.projects_file,
            students_file=args.students_file,
            dry_run=args.dry_run
        )
    finally:
        await client.close()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main()) 