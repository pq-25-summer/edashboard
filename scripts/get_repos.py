#!/usr/bin/env python3
"""
从GitHub Issue抓取项目列表和学生列表
目标: https://github.com/xinase/PQ/issues/3
"""

import httpx    
import re
import json
from typing import List, Tuple, Dict
from dataclasses import dataclass
import os


@dataclass
class Student:
    name: str
    github_id: str
    github_url: str

@dataclass
class Project:
    name: str
    github_url: str
    students: List[Student]


class GitHubIssueScraper:
    def __init__(self, token: str = None):
        self.token = token
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "edashboard-scraper/1.0"
        }
        if token:
            self.headers["Authorization"] = f"token {token}"
    
    def get_issue_content(self, owner: str, repo: str, issue_number: int) -> str:
        """获取GitHub Issue的内容和评论"""
        # 获取Issue主体内容
        issue_url = f"https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}"
        
        try:
            response = httpx.get(issue_url, headers=self.headers)
            response.raise_for_status()
            
            issue_data = response.json()
            content = issue_data.get("body", "")
            
            # 获取Issue评论
            comments_url = f"https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}/comments"
            response = httpx.get(comments_url, headers=self.headers)
            response.raise_for_status()
            
            comments = response.json()
            
            # 将所有评论内容添加到主体内容中
            for comment in comments:
                content += "\n\n" + comment.get("body", "")
            
            return content
        except httpx.exceptions.RequestException as e:
            print(f"获取Issue失败: {e}")
            return ""
    
    def parse_issue_content(self, content: str) -> List[Project]:
        """解析Issue内容，提取项目和学生信息"""
        projects = []
        
        # 查找所有团队信息块
        # 使用正则表达式匹配团队信息提交的格式
        team_blocks = re.findall(
            r'##\s*团队信息提交.*?(?=##\s*团队信息提交|\Z)',
            content,
            re.DOTALL | re.IGNORECASE
        )
        
        for block in team_blocks:
            project = self._parse_team_block(block)
            if project:
                projects.append(project)
        
        return projects
    
    def _parse_team_block(self, block: str) -> Project:
        """解析单个团队信息块"""
        # 提取项目仓库链接
        repo_url_match = re.search(r'\*\*团队项目仓库：\*\*\s*(https://github\.com/[^/\s]+/[^/\s]+)', block)
        if not repo_url_match:
            return None
        
        project_github_url = repo_url_match.group(1)
        
        # 从GitHub URL提取仓库名作为项目名称
        project_name = self._extract_repo_name(project_github_url)
        
        # 提取学生信息
        students = []
        
        # 查找表格中的学生信息
        # 匹配格式：| 成员姓名 | 个人 GitHub ID | 个人 GitHub 链接 |
        table_pattern = r'\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|'
        table_matches = re.findall(table_pattern, block)
        
        for match in table_matches:
            student_name = match[0].strip()
            github_id = match[1].strip()
            student_github_url = match[2].strip()
            
            # 过滤掉表头
            if student_name.lower() in ['成员姓名', '姓名', 'name']:
                continue
            
            # 过滤掉空行
            if not student_name or student_name == '---':
                continue
            
            # 清理学生姓名（移除可能的markdown格式）
            student_name = re.sub(r'[*`]', '', student_name).strip()
            
            # 清理GitHub ID（移除可能的markdown格式）
            github_id = re.sub(r'[*`]', '', github_id).strip()
            
            # 清理GitHub URL（移除可能的markdown格式）
            student_github_url = re.sub(r'[*`]', '', student_github_url).strip()
            
            # 如果GitHub URL为空，尝试从GitHub ID构建
            if not student_github_url and github_id:
                student_github_url = f"https://github.com/{github_id}"
            
            if student_name and self._is_valid_name(student_name):
                students.append(Student(
                    name=student_name,
                    github_id=github_id,
                    github_url=student_github_url
                ))
        
        return Project(
            name=project_name,
            github_url=project_github_url,
            students=students
        )
    
    def _extract_repo_name(self, github_url: str) -> str:
        """从GitHub URL提取仓库名"""
        # 匹配格式：https://github.com/owner/repo
        repo_match = re.search(r'github\.com/[^/]+/([^/\s]+)', github_url)
        if repo_match:
            repo_name = repo_match.group(1)
            # 移除.git后缀
            repo_name = repo_name.replace('.git', '')
            return repo_name
        
        return "unknown-repo"
    
    def _extract_project_name(self, github_url: str, context_line: str) -> str:
        """从GitHub URL或上下文提取项目名称"""
        # 从URL提取repo名称
        repo_match = re.search(r'github\.com/[^/]+/([^/\s]+)', github_url)
        if repo_match:
            repo_name = repo_match.group(1)
            # 移除.git后缀
            repo_name = repo_name.replace('.git', '')
            return repo_name
        
        # 如果无法从URL提取，尝试从上下文提取
        # 查找可能的项目名称模式
        name_match = re.search(r'[A-Za-z0-9_-]+项目', context_line)
        if name_match:
            return name_match.group(0)
        
        return "未知项目"
    
    def _is_valid_name(self, name: str) -> bool:
        """验证是否为有效的姓名"""
        # 过滤掉一些常见的非姓名词汇
        invalid_words = {
            '项目', '小组', '团队', '成员', '组长', '组员', '同学', '学生',
            'Project', 'Group', 'Team', 'Member', 'Student', 'Class',
            'https', 'github', 'com', 'org', 'www', 'http'
        }
        
        if name.lower() in invalid_words:
            return False
        
        # 过滤掉纯数字
        if name.isdigit():
            return False
        
        # 过滤掉过短的名称
        if len(name) < 2:
            return False
        
        # 过滤掉只包含分隔符的名称
        if re.match(r'^[-_=*]+$', name):
            return False
        
        # 过滤掉包含过多特殊字符的名称
        if len(re.findall(r'[-_=*]', name)) > len(name) * 0.5:
            return False
        
        return True
    
    def save_to_files(self, projects: List[Project]):
        """保存项目和学生信息到文件"""
        # 保存项目列表
        with open('projects.txt', 'w', encoding='utf-8') as f:
            for project in projects:
                f.write(f"{project.name}\t{project.github_url}\n")
        
        # 保存学生列表（包含GitHub信息）
        students_dict = {}  # 使用字典去重，以姓名为key
        for project in projects:
            for student in project.students:
                if student.name not in students_dict:
                    students_dict[student.name] = student
                # 如果已存在，保留更完整的GitHub信息
                elif not students_dict[student.name].github_id and student.github_id:
                    students_dict[student.name] = student
        
        with open('students.txt', 'w', encoding='utf-8') as f:
            for student in sorted(students_dict.values(), key=lambda s: s.name):
                if student.name.strip():  # 过滤空字符串
                    f.write(f"{student.name}\t{student.github_id}\t{student.github_url}\n")
        
        print(f"已保存 {len(projects)} 个项目到 projects.txt")
        print(f"已保存 {len(students_dict)} 个学生到 students.txt")
    
    def print_summary(self, projects: List[Project]):
        """打印摘要信息"""
        print("\n=== 项目摘要 ===")
        for i, project in enumerate(projects, 1):
            print(f"{i}. {project.name}")
            print(f"   URL: {project.github_url}")
            if project.students:
                print("   学生:")
                for student in project.students:
                    print(f"     - {student.name} (@{student.github_id}) - {student.github_url}")
            else:
                print("   学生: 未知")
            print()


def main():
    """主函数"""
    # 配置信息
    OWNER = "xinase"
    REPO = "PQ"
    ISSUE_NUMBER = 3
    
    # 从环境变量获取GitHub token (可选)
    github_token = os.getenv('GITHUB_TOKEN')
    
    print("开始抓取GitHub Issue...")
    print(f"目标: https://github.com/{OWNER}/{REPO}/issues/{ISSUE_NUMBER}")
    
    # 创建抓取器
    scraper = GitHubIssueScraper(token=github_token)
    
    # 获取Issue内容
    content = scraper.get_issue_content(OWNER, REPO, ISSUE_NUMBER)
    if not content:
        print("无法获取Issue内容")
        return
    
    print("成功获取Issue内容")
    
    # 解析内容
    projects = scraper.parse_issue_content(content)
    if not projects:
        print("未找到项目信息")
        return
    
    print(f"找到 {len(projects)} 个项目")
    
    # 打印摘要
    scraper.print_summary(projects)
    
    # 保存到文件
    scraper.save_to_files(projects)
    
    print("抓取完成！")


if __name__ == "__main__":
    main() 