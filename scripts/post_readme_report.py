#!/usr/bin/env python3
"""
将README检查结果发布到GitHub Issue

从check_readme.py的结果生成报告并发布到指定的GitHub Issue。
"""

import os
import sys
import argparse
import json
from pathlib import Path
from typing import Dict, Optional
import logging

# 尝试导入httpx，如果不存在则提示安装
try:
    import httpx
except ImportError:
    print("错误: 需要安装httpx库")
    print("请运行: pip install httpx")
    sys.exit(1)


class GitHubIssuePoster:
    def __init__(self, token: str = None):
        self.token = token or os.getenv('GITHUB_TOKEN')
        if not self.token:
            raise ValueError("需要提供GitHub Token (通过参数或GITHUB_TOKEN环境变量)")
        
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "Authorization": f"token {self.token}",
            "User-Agent": "edashboard-readme-checker/1.0"
        }
    
    def post_comment(self, owner: str, repo: str, issue_number: int, body: str) -> bool:
        """发布评论到GitHub Issue"""
        url = f"https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}/comments"
        
        try:
            response = httpx.post(
                url,
                headers=self.headers,
                json={"body": body},
                timeout=30
            )
            response.raise_for_status()
            
            comment_data = response.json()
            print(f"✅ 成功发布评论到 Issue #{issue_number}")
            print(f"评论URL: {comment_data.get('html_url', 'N/A')}")
            return True
            
        except httpx.HTTPStatusError as e:
            print(f"❌ 发布评论失败: {e}")
            print(f"响应状态码: {e.response.status_code}")
            print(f"响应内容: {e.response.text}")
            return False
        except httpx.RequestError as e:
            print(f"❌ 网络请求失败: {e}")
            return False
    
    def get_issue(self, owner: str, repo: str, issue_number: int) -> Optional[Dict]:
        """获取Issue信息"""
        url = f"https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}"
        
        try:
            response = httpx.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            return response.json()
            
        except httpx.HTTPStatusError as e:
            print(f"❌ 获取Issue失败: {e}")
            return None
        except httpx.RequestError as e:
            print(f"❌ 网络请求失败: {e}")
            return None


def load_readme_results(results_file: str) -> Dict:
    """从文件加载README检查结果"""
    try:
        with open(results_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # 如果数据包含summary和results结构，提取results部分
            if 'results' in data and 'summary' in data:
                return data['results']
            # 否则直接返回数据
            return data
    except Exception as e:
        print(f"❌ 加载结果文件失败: {e}")
        return {}


def generate_issue_comment(results: Dict, summary: Dict) -> str:
    """生成Issue评论内容"""
    comment = []
    
    # 标题
    comment.append("# 📊 README文档检查报告")
    comment.append("")
    
    # 摘要
    comment.append("## 统计摘要")
    comment.append("")
    comment.append(f"- **总项目数**: {summary['total_repos']}")
    comment.append(f"- **包含README的项目**: {summary['repos_with_readme']}")
    comment.append(f"- **不包含README的项目**: {summary['repos_without_readme']}")
    comment.append(f"- **README覆盖率**: {summary['readme_coverage']}%")
    comment.append("")
    
    # README文件类型分布
    if summary['readme_types']:
        comment.append("### README文件类型分布")
        comment.append("")
        for ext, count in summary['readme_types'].items():
            ext_name = ext if ext else "(无扩展名)"
            comment.append(f"- {ext_name}: {count} 个")
        comment.append("")
    
    # 详细结果
    comment.append("## 详细结果")
    comment.append("")
    
    # 按是否有README分组
    with_readme = []
    without_readme = []
    
    for project_key, info in results.items():
        if info['has_readme']:
            with_readme.append((project_key, info))
        else:
            without_readme.append((project_key, info))
    
    # 有README的项目
    if with_readme:
        comment.append("### ✅ 包含README的项目")
        comment.append("")
        for project_key, info in sorted(with_readme):
            readme_names = [f['name'] for f in info['readme_files']]
            comment.append(f"- **{project_key}**: {', '.join(readme_names)}")
        comment.append("")
    
    # 没有README的项目
    if without_readme:
        comment.append("### ❌ 不包含README的项目")
        comment.append("")
        for project_key, info in sorted(without_readme):
            comment.append(f"- **{project_key}**")
        comment.append("")
    
    # 建议
    comment.append("## 💡 建议")
    comment.append("")
    if without_readme:
        comment.append("建议以下项目添加README文档:")
        comment.append("")
        for project_key, info in sorted(without_readme):
            comment.append(f"- {project_key}")
        comment.append("")
        comment.append("README文档应包含:")
        comment.append("- 项目简介和功能说明")
        comment.append("- 安装和使用方法")
        comment.append("- 技术栈和依赖")
        comment.append("- 贡献指南")
    else:
        comment.append("🎉 所有项目都包含README文档！")
    
    # 时间戳
    from datetime import datetime
    comment.append("")
    comment.append("---")
    comment.append(f"*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
    
    return "\n".join(comment)


def main():
    parser = argparse.ArgumentParser(
        description="将README检查结果发布到GitHub Issue",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python post_readme_report.py --owner pq-25-summer --repo edashboard --issue 1 --results results.json
  python post_readme_report.py --owner pq-25-summer --repo edashboard --issue 1 --results results.json --token your_token
        """
    )
    
    parser.add_argument(
        '--owner',
        required=True,
        help='GitHub仓库所有者'
    )
    
    parser.add_argument(
        '--repo',
        required=True,
        help='GitHub仓库名称'
    )
    
    parser.add_argument(
        '--issue',
        type=int,
        required=True,
        help='Issue编号'
    )
    
    parser.add_argument(
        '--results',
        required=True,
        help='README检查结果JSON文件'
    )
    
    parser.add_argument(
        '--token',
        help='GitHub Token (也可通过GITHUB_TOKEN环境变量设置)'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='预览模式，不实际发布评论'
    )
    
    args = parser.parse_args()
    
    # 检查结果文件
    if not Path(args.results).exists():
        print(f"❌ 结果文件不存在: {args.results}")
        sys.exit(1)
    
    # 加载结果
    results = load_readme_results(args.results)
    if not results:
        print("❌ 无法加载检查结果")
        sys.exit(1)
    
    # 生成摘要
    total_repos = len(results)
    repos_with_readme = sum(1 for info in results.values() if info['has_readme'])
    repos_without_readme = total_repos - repos_with_readme
    
    # 统计README文件类型
    readme_types = {}
    for info in results.values():
        for readme_file in info['readme_files']:
            ext = Path(readme_file['name']).suffix.lower()
            readme_types[ext] = readme_types.get(ext, 0) + 1
    
    summary = {
        'total_repos': total_repos,
        'repos_with_readme': repos_with_readme,
        'repos_without_readme': repos_without_readme,
        'readme_coverage': round(repos_with_readme / total_repos * 100, 1) if total_repos > 0 else 0,
        'readme_types': readme_types
    }
    
    # 生成评论内容
    comment_body = generate_issue_comment(results, summary)
    
    if args.dry_run:
        print("🔍 预览模式 - 评论内容:")
        print("=" * 60)
        print(comment_body)
        print("=" * 60)
        return
    
    # 创建GitHub客户端
    try:
        poster = GitHubIssuePoster(args.token)
    except ValueError as e:
        print(f"❌ {e}")
        sys.exit(1)
    
    # 验证Issue存在
    issue = poster.get_issue(args.owner, args.repo, args.issue)
    if not issue:
        print(f"❌ 无法访问Issue #{args.issue}")
        sys.exit(1)
    
    print(f"📋 找到Issue: {issue.get('title', 'N/A')}")
    print(f"🔗 Issue URL: {issue.get('html_url', 'N/A')}")
    
    # 发布评论
    success = poster.post_comment(args.owner, args.repo, args.issue, comment_body)
    
    if success:
        print("✅ 评论发布成功！")
        sys.exit(0)
    else:
        print("❌ 评论发布失败")
        sys.exit(1)


if __name__ == '__main__':
    main() 