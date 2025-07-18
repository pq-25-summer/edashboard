#!/usr/bin/env python3
"""
调试脚本：查看GitHub Issue的原始内容和评论
"""

import requests
import os
import json


def get_issue_content(owner: str, repo: str, issue_number: int, token: str = None):
    """获取GitHub Issue的内容"""
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "edashboard-scraper/1.0"
    }
    if token:
        headers["Authorization"] = f"token {token}"
    
    url = f"https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}"
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        issue_data = response.json()
        
        print("=== Issue 基本信息 ===")
        print(f"标题: {issue_data.get('title', 'N/A')}")
        print(f"状态: {issue_data.get('state', 'N/A')}")
        print(f"创建者: {issue_data.get('user', {}).get('login', 'N/A')}")
        print(f"创建时间: {issue_data.get('created_at', 'N/A')}")
        print(f"更新时间: {issue_data.get('updated_at', 'N/A')}")
        print(f"评论数: {issue_data.get('comments', 0)}")
        print()
        
        print("=== Issue 内容 ===")
        content = issue_data.get("body", "")
        print(content)
        print()
        
        print("=== 内容长度 ===")
        print(f"字符数: {len(content)}")
        print(f"行数: {len(content.split(chr(10)))}")
        
        # 保存原始内容到文件
        with open('issue_content.txt', 'w', encoding='utf-8') as f:
            f.write(content)
        print("\n原始内容已保存到 issue_content.txt")
        
        return content
        
    except requests.exceptions.RequestException as e:
        print(f"获取Issue失败: {e}")
        return ""


def get_issue_comments(owner: str, repo: str, issue_number: int, token: str = None):
    """获取GitHub Issue的评论"""
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "edashboard-scraper/1.0"
    }
    if token:
        headers["Authorization"] = f"token {token}"
    
    url = f"https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}/comments"
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        comments = response.json()
        
        print(f"=== Issue 评论 (共 {len(comments)} 条) ===")
        
        all_comments_content = ""
        
        for i, comment in enumerate(comments, 1):
            print(f"\n--- 评论 {i} ---")
            print(f"作者: {comment.get('user', {}).get('login', 'N/A')}")
            print(f"时间: {comment.get('created_at', 'N/A')}")
            print(f"内容:")
            comment_content = comment.get('body', '')
            print(comment_content)
            print("-" * 50)
            
            all_comments_content += f"\n--- 评论 {i} ---\n"
            all_comments_content += f"作者: {comment.get('user', {}).get('login', 'N/A')}\n"
            all_comments_content += f"时间: {comment.get('created_at', 'N/A')}\n"
            all_comments_content += f"内容:\n{comment_content}\n"
            all_comments_content += "-" * 50 + "\n"
        
        # 保存所有评论到文件
        with open('issue_comments.txt', 'w', encoding='utf-8') as f:
            f.write(all_comments_content)
        print(f"\n所有评论已保存到 issue_comments.txt")
        
        return comments
        
    except requests.exceptions.RequestException as e:
        print(f"获取评论失败: {e}")
        return []


if __name__ == "__main__":
    OWNER = "xinase"
    REPO = "PQ"
    ISSUE_NUMBER = 3
    
    github_token = os.getenv('GITHUB_TOKEN')
    
    print("调试GitHub Issue内容和评论...")
    print(f"目标: https://github.com/{OWNER}/{REPO}/issues/{ISSUE_NUMBER}")
    print()
    
    # 获取Issue内容
    content = get_issue_content(OWNER, REPO, ISSUE_NUMBER, github_token)
    
    # 获取Issue评论
    comments = get_issue_comments(OWNER, REPO, ISSUE_NUMBER, github_token) 