#!/usr/bin/env python3
"""
Git工作流程分析脚本
独立分析各项目的Git使用风格
"""

import os
import sys
import json
import argparse
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict

# 添加backend目录到Python路径
sys.path.append(str(Path(__file__).parent.parent / "backend"))

from app.git_workflow_analyzer import GitWorkflowAnalyzer, GitWorkflowStats
from app.database import get_db

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_projects_from_db() -> List[Dict]:
    """从数据库加载项目列表"""
    try:
        import asyncio
        
        async def fetch_projects():
            async with get_db() as db:
                projects_result = await db.fetch("SELECT name, github_url FROM projects")
                return [{"name": row["name"], "github_url": row["github_url"]} for row in projects_result]
        
        return asyncio.run(fetch_projects())
    except Exception as e:
        logger.error(f"从数据库加载项目失败: {e}")
        return []


def load_projects_from_file(file_path: str) -> List[Dict]:
    """从文件加载项目列表"""
    try:
        projects = []
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and '\t' in line:
                    name, github_url = line.split('\t', 1)
                    projects.append({"name": name, "github_url": github_url})
        return projects
    except Exception as e:
        logger.error(f"从文件加载项目失败: {e}")
        return []


def save_results_to_file(results: List[GitWorkflowStats], output_file: str):
    """保存分析结果到文件"""
    try:
        data = []
        for result in results:
            data.append({
                "project_name": result.project_name,
                "github_url": result.github_url,
                "total_branches": result.total_branches,
                "main_branch_name": result.main_branch_name,
                "feature_branches": result.feature_branches,
                "hotfix_branches": result.hotfix_branches,
                "total_commits": result.total_commits,
                "commits_on_main": result.commits_on_main,
                "commits_on_branches": result.commits_on_branches,
                "merge_commits": result.merge_commits,
                "rebase_commits": result.rebase_commits,
                "has_pull_requests": result.has_pull_requests,
                "pull_request_count": result.pull_request_count,
                "merged_pull_requests": result.merged_pull_requests,
                "uses_feature_branches": result.uses_feature_branches,
                "uses_main_branch_merges": result.uses_main_branch_merges,
                "uses_rebase": result.uses_rebase,
                "uses_pull_requests": result.uses_pull_requests,
                "workflow_score": result.workflow_score,
                "workflow_style": result.workflow_style,
                "analyzed_at": result.analyzed_at.isoformat()
            })
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"分析结果已保存到: {output_file}")
        
    except Exception as e:
        logger.error(f"保存结果失败: {e}")


def generate_summary_report(results: List[GitWorkflowStats]) -> Dict:
    """生成摘要报告"""
    if not results:
        return {
            "total_projects": 0,
            "message": "没有分析结果"
        }
    
    total_projects = len(results)
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
    
    return {
        "total_projects": total_projects,
        "workflow_statistics": {
            "workflow_styles": workflow_styles,
            "feature_branch_usage": {
                "count": feature_branch_usage,
                "percentage": round(feature_branch_usage / total_projects * 100, 1) if total_projects > 0 else 0
            },
            "merge_usage": {
                "count": merge_usage,
                "percentage": round(merge_usage / total_projects * 100, 1) if total_projects > 0 else 0
            },
            "rebase_usage": {
                "count": rebase_usage,
                "percentage": round(rebase_usage / total_projects * 100, 1) if total_projects > 0 else 0
            },
            "pull_request_usage": {
                "count": pr_usage,
                "percentage": round(pr_usage / total_projects * 100, 1) if total_projects > 0 else 0
            },
            "average_score": round(avg_score, 1)
        },
        "analysis_time": datetime.now().isoformat()
    }


def print_summary_report(summary: Dict):
    """打印摘要报告"""
    print("\n" + "="*60)
    print("Git工作流程分析报告")
    print("="*60)
    
    print(f"总项目数: {summary['total_projects']}")
    print(f"分析时间: {summary['analysis_time']}")
    
    if summary['total_projects'] == 0:
        print("没有分析结果")
        return
    
    stats = summary['workflow_statistics']
    print(f"\n平均评分: {stats['average_score']}")
    
    print("\n工作流程风格分布:")
    for style, count in stats['workflow_styles'].items():
        percentage = round(count / summary['total_projects'] * 100, 1)
        print(f"  {style}: {count}个项目 ({percentage}%)")
    
    print("\nGit功能使用情况:")
    print(f"  功能分支: {stats['feature_branch_usage']['count']}个项目 ({stats['feature_branch_usage']['percentage']}%)")
    print(f"  分支合并: {stats['merge_usage']['count']}个项目 ({stats['merge_usage']['percentage']}%)")
    print(f"  Rebase操作: {stats['rebase_usage']['count']}个项目 ({stats['rebase_usage']['percentage']}%)")
    print(f"  Pull Request: {stats['pull_request_usage']['count']}个项目 ({stats['pull_request_usage']['percentage']}%)")


def print_detailed_results(results: List[GitWorkflowStats]):
    """打印详细结果"""
    print("\n" + "="*100)
    print("详细分析结果")
    print("="*100)
    
    # 按评分排序
    sorted_results = sorted(results, key=lambda x: x.workflow_score, reverse=True)
    
    print(f"{'项目名称':<20} {'工作流程风格':<20} {'评分':<8} {'分支数':<8} {'提交数':<8} {'功能分支':<8} {'合并':<6} {'Rebase':<8} {'PR':<6}")
    print("-" * 100)
    
    for result in sorted_results:
        print(f"{result.project_name:<20} {result.workflow_style:<20} {result.workflow_score:<8.1f} {result.total_branches:<8} {result.total_commits:<8} "
              f"{'是' if result.uses_feature_branches else '否':<8} {'是' if result.uses_main_branch_merges else '否':<6} "
              f"{'是' if result.uses_rebase else '否':<8} {'是' if result.uses_pull_requests else '否':<6}")


def main():
    parser = argparse.ArgumentParser(description="Git工作流程分析脚本")
    parser.add_argument("--projects-file", help="项目列表文件路径 (projects.txt)")
    parser.add_argument("--repos-path", default="repos", help="本地仓库路径")
    parser.add_argument("--output", default="git_workflow_analysis.json", help="输出文件路径")
    parser.add_argument("--summary-only", action="store_true", help="只显示摘要报告")
    parser.add_argument("--verbose", action="store_true", help="显示详细日志")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    logger.info("开始Git工作流程分析")
    
    # 加载项目列表
    projects = []
    if args.projects_file:
        projects = load_projects_from_file(args.projects_file)
        logger.info(f"从文件加载了 {len(projects)} 个项目")
    else:
        projects = load_projects_from_db()
        logger.info(f"从数据库加载了 {len(projects)} 个项目")
    
    if not projects:
        logger.error("没有找到项目")
        return 1
    
    # 创建分析器
    analyzer = GitWorkflowAnalyzer(projects_base_path=args.repos_path)
    
    # 分析项目
    logger.info("开始分析项目...")
    results = analyzer.analyze_all_projects(projects)
    
    if not results:
        logger.warning("没有成功分析任何项目")
        return 1
    
    logger.info(f"成功分析了 {len(results)} 个项目")
    
    # 生成摘要报告
    summary = generate_summary_report(results)
    
    # 打印报告
    print_summary_report(summary)
    
    if not args.summary_only:
        print_detailed_results(results)
    
    # 保存结果
    save_results_to_file(results, args.output)
    
    # 保存摘要报告
    summary_file = args.output.replace('.json', '_summary.json')
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    
    logger.info(f"摘要报告已保存到: {summary_file}")
    logger.info("Git工作流程分析完成")
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 