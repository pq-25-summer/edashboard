#!/usr/bin/env python3
"""
学生-项目关联脚本
基于GitHub用户名将学生与项目关联起来
"""

import asyncio
import httpx
import sys
import os
from typing import Dict, List, Optional

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class StudentProjectAssociator:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient()
    
    async def get_all_projects(self) -> List[Dict]:
        """获取所有项目"""
        response = await self.client.get(f"{self.base_url}/api/projects/")
        if response.status_code == 200:
            return response.json()
        else:
            print(f"获取项目失败: {response.status_code}")
            return []
    
    async def get_all_students(self) -> List[Dict]:
        """获取所有学生"""
        response = await self.client.get(f"{self.base_url}/api/students/")
        if response.status_code == 200:
            return response.json()
        else:
            print(f"获取学生失败: {response.status_code}")
            return []
    
    def extract_owner_from_url(self, github_url: str) -> Optional[str]:
        """从GitHub URL提取owner"""
        try:
            if github_url.startswith("https://github.com/"):
                parts = github_url.replace("https://github.com/", "").split("/")
                if len(parts) >= 1:
                    return parts[0]
        except Exception as e:
            print(f"解析GitHub URL失败: {e}")
        return None
    
    def match_student_to_project(self, student: Dict, projects: List[Dict]) -> Optional[int]:
        """尝试将学生匹配到项目"""
        github_username = student.get("github_username")
        if not github_username:
            return None
        
        # 方法1: 直接匹配GitHub用户名作为项目owner
        for project in projects:
            owner = self.extract_owner_from_url(project["github_url"])
            if owner and owner.lower() == github_username.lower():
                return project["id"]
        
        # 方法2: 检查项目URL中是否包含学生用户名
        for project in projects:
            github_url = project["github_url"].lower()
            if github_username.lower() in github_url:
                return project["id"]
        
        return None
    
    async def update_student_project(self, student_id: int, project_id: int) -> bool:
        """更新学生的项目ID"""
        # 获取学生当前信息
        response = await self.client.get(f"{self.base_url}/api/students/{student_id}")
        if response.status_code != 200:
            return False
        
        student_data = response.json()
        
        # 更新学生信息
        update_data = {
            "name": student_data["name"],
            "github_username": student_data["github_username"],
            "email": student_data["email"],
            "project_id": project_id
        }
        
        response = await self.client.put(f"{self.base_url}/api/students/{student_id}", json=update_data)
        return response.status_code == 200
    
    async def associate_students_to_projects(self, dry_run: bool = False):
        """关联学生到项目"""
        print("🔍 开始学生-项目关联...")
        
        # 获取所有项目和学生
        projects = await self.get_all_projects()
        students = await self.get_all_students()
        
        print(f"📊 找到 {len(projects)} 个项目，{len(students)} 个学生")
        
        if not projects or not students:
            print("❌ 没有找到项目或学生数据")
            return
        
        # 统计信息
        matched_count = 0
        unmatched_count = 0
        matched_students = []
        unmatched_students = []
        
        for student in students:
            project_id = self.match_student_to_project(student, projects)
            if project_id:
                matched_count += 1
                matched_students.append((student, project_id))
                project_name = next((p["name"] for p in projects if p["id"] == project_id), "未知")
                print(f"✅ {student['name']} ({student['github_username']}) -> {project_name}")
            else:
                unmatched_count += 1
                unmatched_students.append(student)
                print(f"❌ {student['name']} ({student['github_username']}) -> 未匹配")
        
        print(f"\n📈 匹配结果:")
        print(f"   ✅ 匹配成功: {matched_count} 个学生")
        print(f"   ❌ 未匹配: {unmatched_count} 个学生")
        
        if dry_run:
            print("\n🔍 这是预览模式，不会实际更新数据库")
            return
        
        # 实际更新数据库
        if matched_students:
            print(f"\n💾 开始更新数据库...")
            updated_count = 0
            
            for student, project_id in matched_students:
                if await self.update_student_project(student["id"], project_id):
                    updated_count += 1
                    print(f"   ✅ 更新成功: {student['name']} -> 项目ID {project_id}")
                else:
                    print(f"   ❌ 更新失败: {student['name']}")
            
            print(f"\n🎉 数据库更新完成: {updated_count}/{matched_count} 个学生关联成功")
        
        # 显示未匹配的学生
        if unmatched_students:
            print(f"\n⚠️  未匹配的学生 ({len(unmatched_students)} 个):")
            for student in unmatched_students[:10]:  # 只显示前10个
                print(f"   - {student['name']} ({student['github_username']})")
            if len(unmatched_students) > 10:
                print(f"   ... 还有 {len(unmatched_students) - 10} 个学生未匹配")
    
    async def close(self):
        """关闭客户端"""
        await self.client.aclose()


async def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="学生-项目关联脚本")
    parser.add_argument("--base-url", default="http://localhost:8000", help="API基础URL")
    parser.add_argument("--dry-run", action="store_true", help="预览模式，不实际更新数据库")
    
    args = parser.parse_args()
    
    associator = StudentProjectAssociator(args.base_url)
    
    try:
        await associator.associate_students_to_projects(dry_run=args.dry_run)
    finally:
        await associator.close()


if __name__ == "__main__":
    asyncio.run(main()) 