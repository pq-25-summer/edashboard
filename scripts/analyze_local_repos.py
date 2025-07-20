#!/usr/bin/env python3
"""
分析本地Git仓库的Git工作流程
遍历repos/*/*目录结构，分析每个Git仓库的工作流程
"""

import os
import sys
import subprocess
import traceback
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

# 添加backend目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

try:
    from app.git_workflow_analyzer import GitWorkflowAnalyzer, GitWorkflowStats
except ImportError as e:
    print(f"❌ 导入Git工作流程分析器失败: {e}")
    print("请确保backend/app/git_workflow_analyzer.py文件存在")
    sys.exit(1)


def find_git_repos(repos_base_path: str) -> List[Dict]:
    """查找所有Git仓库"""
    repos_dir = Path(repos_base_path)
    projects = []
    
    if not repos_dir.exists():
        print(f"❌ 本地仓库目录不存在: {repos_base_path}")
        return projects
    
    print(f"🔍 扫描目录: {repos_base_path}")
    
    for owner_dir in repos_dir.iterdir():
        if owner_dir.is_dir():
            print(f"  📁 检查组织/用户: {owner_dir.name}")
            for repo_dir in owner_dir.iterdir():
                if repo_dir.is_dir():
                    git_dir = repo_dir / '.git'
                    if git_dir.exists() and git_dir.is_dir():
                        # 这是一个Git仓库
                        owner = owner_dir.name
                        repo = repo_dir.name
                        project_name = f"{owner}/{repo}"
                        github_url = f"https://github.com/{owner}/{repo}"
                        
                        projects.append({
                            'name': project_name,
                            'github_url': github_url,
                            'local_path': str(repo_dir),
                            'owner': owner,
                            'repo': repo
                        })
                        print(f"    ✅ 找到Git仓库: {project_name}")
                    else:
                        print(f"    ⚠️ 跳过非Git目录: {repo_dir.name}")
    
    return projects


def analyze_repos(projects: List[Dict], repos_base_path: str) -> List[GitWorkflowStats]:
    """分析所有仓库的Git工作流程"""
    analyzer = GitWorkflowAnalyzer(projects_base_path=repos_base_path)
    results = []
    
    print(f"\n🔍 开始分析 {len(projects)} 个Git仓库...")
    
    for i, project in enumerate(projects, 1):
        print(f"\n[{i}/{len(projects)}] 分析: {project['name']}")
        print(f"    📂 本地路径: {project['local_path']}")
        
        try:
            result = analyzer.analyze_project(project['name'], project['github_url'])
            if result:
                results.append(result)
                print(f"    ✅ 分析完成 - 风格: {result.workflow_style}, 评分: {result.workflow_score:.1f}")
            else:
                print(f"    ❌ 分析失败")
        except Exception as e:
            print(f"    ❌ 分析出错: {e}")
    
    return results


def generate_report(results: List[GitWorkflowStats]) -> str:
    """生成分析报告"""
    if not results:
        return "❌ 没有分析结果"
    
    total_projects = len(results)
    
    # 统计工作流程风格
    workflow_styles = {}
    feature_branch_usage = 0
    merge_usage = 0
    rebase_usage = 0
    pr_usage = 0
    total_score = 0
    
    for result in results:
        # 工作流程风格统计
        style = result.workflow_style
        workflow_styles[style] = workflow_styles.get(style, 0) + 1
        
        # 功能使用统计
        if result.uses_feature_branches:
            feature_branch_usage += 1
        if result.uses_main_branch_merges:
            merge_usage += 1
        if result.uses_rebase:
            rebase_usage += 1
        if result.uses_pull_requests:
            pr_usage += 1
        
        total_score += result.workflow_score
    
    avg_score = total_score / total_projects if total_projects > 0 else 0
    
    # 生成报告
    report = f"""# Git工作流程分析报告

## 📊 总体统计

**分析时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**总项目数**: {total_projects}个  
**平均评分**: {avg_score:.1f}分

## 🎯 Issue 3 任务完成情况

根据Issue 3的要求，我们分析了各项目的Git使用风格，包括：

### ✅ 分析维度

1. **是否基于主分支合并commit** - 通过分析合并提交数量
2. **是否基于branch写作** - 通过分析功能分支使用情况  
3. **是否使用 pull request** - 通过分析Pull Request使用情况
4. **是否使用 rebase模式** - 通过分析Rebase操作使用情况

## 📈 详细统计

### 工作流程风格分布

"""
    
    for style, count in workflow_styles.items():
        percentage = round(count / total_projects * 100, 1)
        report += f"- **{style}**: {count}个项目 ({percentage}%)\n"
    
    report += f"""
### Git功能使用情况

- **功能分支使用**: {feature_branch_usage}个项目 ({round(feature_branch_usage/total_projects*100, 1)}%)
- **分支合并使用**: {merge_usage}个项目 ({round(merge_usage/total_projects*100, 1)}%)
- **Rebase操作使用**: {rebase_usage}个项目 ({round(rebase_usage/total_projects*100, 1)}%)
- **Pull Request使用**: {pr_usage}个项目 ({round(pr_usage/total_projects*100, 1)}%)

## 🏆 项目详细分析

按Git工作流程评分从高到低排序：

| 排名 | 项目名称 | 工作流程风格 | 评分 | 功能分支 | 分支合并 | Rebase | Pull Request |
|------|----------|--------------|------|----------|----------|--------|--------------|
"""
    
    # 按评分排序
    sorted_results = sorted(results, key=lambda x: x.workflow_score, reverse=True)
    
    for i, result in enumerate(sorted_results, 1):
        report += f"| {i} | [{result.project_name}]({result.github_url}) | {result.workflow_style} | {result.workflow_score:.1f} | {'✅' if result.uses_feature_branches else '❌'} | {'✅' if result.uses_main_branch_merges else '❌'} | {'✅' if result.uses_rebase else '❌'} | {'✅' if result.uses_pull_requests else '❌'} |\n"
    
    report += """
## 📋 分析说明

### 评分标准
- **功能分支开发**: +20分
- **分支合并操作**: +15分  
- **Rebase操作**: +10分
- **Pull Request使用**: +25分

### 工作流程风格分类
- **Git Flow (完整工作流)**: 60分以上，使用完整的分支策略
- **Feature Branch (功能分支)**: 40-59分，主要使用功能分支
- **Trunk Based (主干开发)**: 20-39分，主要在主干分支开发
- **Simple (简单模式)**: 20分以下，简单的Git使用

## 🎯 改进建议

基于分析结果，建议各团队：

1. **提高功能分支使用率**: 目前只有{feature_branch_usage}个项目使用功能分支
2. **增加Pull Request使用**: 目前只有{pr_usage}个项目使用Pull Request
3. **学习Rebase操作**: 目前只有{rebase_usage}个项目使用Rebase
4. **规范分支合并流程**: 目前只有{merge_usage}个项目有分支合并操作

## 🔧 技术实现

- 使用Git命令分析本地仓库的分支和提交历史
- 通过GitHub API获取Pull Request信息
- 自动识别工作流程风格并计算评分
- 生成可视化报告和统计数据

---
*此报告由软件工程课看板系统自动生成*
"""
    
    return report


def post_report_to_github(report_content: str, issue_number: int = 3) -> bool:
    """将报告发布到GitHub Issue"""
    try:
        # 保存报告到临时文件
        report_file = "git_workflow_report.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        # 使用gh命令发布评论
        result = subprocess.run(
            ['gh', 'issue', 'comment', str(issue_number), '--body-file', report_file],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        # 清理临时文件
        os.remove(report_file)
        
        if result.returncode == 0:
            print(f"✅ 成功发布报告到 Issue #{issue_number}")
            return True
        else:
            print(f"❌ 发布报告失败: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ 发布报告超时")
        return False
    except Exception as e:
        print(f"❌ 发布报告异常: {e}")
        return False


def main():
    """主函数"""
    print("🚀 开始分析本地Git仓库工作流程...")
    
    # 设置环境变量
    if 'LOCAL_REPOS_DIR' not in os.environ:
        os.environ['LOCAL_REPOS_DIR'] = '/Users/mars/jobs/pq/repos'
    os.environ['DATABASE_URL'] = 'postgresql://localhost/edashboard'
    os.environ['GITHUB_API_BASE_URL'] = 'https://api.github.com'
    os.environ['APP_NAME'] = '软件工程课看板系统'
    os.environ['DEBUG'] = 'true'
    os.environ['SECRET_KEY'] = 'your-secret-key-here-change-in-production'
    os.environ['ALGORITHM'] = 'HS256'
    os.environ['ACCESS_TOKEN_EXPIRE_MINUTES'] = '30'
    
    try:
        # 获取本地仓库路径
        repos_path = os.environ.get('LOCAL_REPOS_DIR', '/Users/mars/jobs/pq/repos')
        
        # 查找所有Git仓库
        projects = find_git_repos(repos_path)
        
        if not projects:
            print("❌ 没有找到任何Git仓库")
            return 1
        
        print(f"\n📋 找到 {len(projects)} 个Git仓库")
        
        # 分析仓库
        results = analyze_repos(projects, repos_path)
        
        if not results:
            print("❌ 没有成功分析任何项目")
            return 1
        
        print(f"\n📊 成功分析 {len(results)} 个项目")
        
        # 生成报告
        print("📝 生成分析报告...")
        report = generate_report(results)
        
        # 保存报告到文件
        report_file = "git_workflow_analysis_report.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"📄 报告已保存到: {report_file}")
        
        # 尝试发布到GitHub Issue
        try:
            post_report_to_github(report)
            print("✅ 报告已发布到GitHub Issue #3")
        except Exception as e:
            print(f"⚠️ 发布到GitHub失败: {e}")
            print("📄 请手动将报告内容复制到Issue #3")
        
        return 0
        
    except Exception as e:
        print(f"❌ 分析过程中出错: {e}")
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main()) 