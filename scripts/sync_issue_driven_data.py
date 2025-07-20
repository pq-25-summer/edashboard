#!/usr/bin/env python3
"""
Issue驱动开发数据同步脚本
将Issue驱动开发分析结果同步到项目状态数据库中
"""

import os
import sys
import json
import argparse
import logging
from typing import Dict, List, Optional
from pathlib import Path
import asyncio

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backend'))

from app.database import db
from app.config import settings

logger = logging.getLogger(__name__)


async def sync_issue_driven_data(analysis_file: str = "issue_driven_analysis.json") -> bool:
    """同步Issue驱动开发数据到数据库"""
    try:
        # 检查分析文件是否存在
        if not os.path.exists(analysis_file):
            logger.error(f"分析文件不存在: {analysis_file}")
            return False
        
        # 读取分析结果
        with open(analysis_file, 'r', encoding='utf-8') as f:
            analysis_data = json.load(f)
        
        logger.info(f"读取到 {len(analysis_data)} 个项目的分析数据")
        
        # 连接到数据库
        async with db.get_db() as conn:
            async with conn.cursor() as cur:
                # 遍历分析结果
                for project_data in analysis_data:
                    project_name = project_data['project_name']
                    github_url = project_data['github_url']
                    
                    logger.info(f"同步项目: {project_name}")
                    
                    # 查找项目ID
                    await cur.execute(
                        "SELECT id FROM projects WHERE github_url = %s",
                        (github_url,)
                    )
                    project_result = await cur.fetchone()
                    
                    if not project_result:
                        logger.warning(f"项目不存在: {project_name} ({github_url})")
                        continue
                    
                    project_id = project_result['id']
                    
                    # 更新项目状态表中的Issue驱动开发数据
                    await cur.execute("""
                        UPDATE project_statuses SET
                            total_issues = %s,
                            commits_with_issue_refs = %s,
                            commits_without_issue_refs = %s,
                            issues_with_assignees = %s,
                            issues_without_assignees = %s,
                            closed_issues = %s,
                            open_issues = %s,
                            commit_issue_ratio = %s,
                            issue_assignee_ratio = %s,
                            issue_closure_ratio = %s,
                            uses_issue_driven_development = %s,
                            issue_driven_score = %s,
                            issue_workflow_quality = %s,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE project_id = %s
                    """, (
                        project_data['total_issues'],
                        project_data['commits_with_issue_refs'],
                        project_data['commits_without_issue_refs'],
                        project_data['issues_with_assignees'],
                        project_data['issues_without_assignees'],
                        project_data['closed_issues'],
                        project_data['open_issues'],
                        project_data['commit_issue_ratio'],
                        project_data['issue_assignee_ratio'],
                        project_data['issue_closure_ratio'],
                        project_data['uses_issue_driven_development'],
                        project_data['issue_driven_score'],
                        project_data['workflow_quality'],
                        project_id
                    ))
                    
                    # 检查是否更新成功
                    if cur.rowcount == 0:
                        logger.warning(f"项目状态记录不存在，创建新记录: {project_name}")
                        # 创建新的项目状态记录
                        await cur.execute("""
                            INSERT INTO project_statuses (
                                project_id,
                                total_issues,
                                commits_with_issue_refs,
                                commits_without_issue_refs,
                                issues_with_assignees,
                                issues_without_assignees,
                                closed_issues,
                                open_issues,
                                commit_issue_ratio,
                                issue_assignee_ratio,
                                issue_closure_ratio,
                                uses_issue_driven_development,
                                issue_driven_score,
                                issue_workflow_quality
                            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """, (
                            project_id,
                            project_data['total_issues'],
                            project_data['commits_with_issue_refs'],
                            project_data['commits_without_issue_refs'],
                            project_data['issues_with_assignees'],
                            project_data['issues_without_assignees'],
                            project_data['closed_issues'],
                            project_data['open_issues'],
                            project_data['commit_issue_ratio'],
                            project_data['issue_assignee_ratio'],
                            project_data['issue_closure_ratio'],
                            project_data['uses_issue_driven_development'],
                            project_data['issue_driven_score'],
                            project_data['workflow_quality']
                        ))
                    
                    logger.info(f"✅ 成功同步项目: {project_name}")
                
                # 提交事务
                await conn.commit()
                
                logger.info(f"🎉 成功同步 {len(analysis_data)} 个项目的Issue驱动开发数据")
                return True
                
    except Exception as e:
        logger.error(f"同步Issue驱动开发数据失败: {e}")
        return False


async def get_sync_summary() -> Dict:
    """获取同步摘要"""
    try:
        async with db.get_db() as conn:
            async with conn.cursor() as cur:
                # 获取项目状态统计
                await cur.execute("""
                    SELECT 
                        COUNT(*) as total_projects,
                        COUNT(CASE WHEN uses_issue_driven_development THEN 1 END) as projects_with_issue_driven,
                        AVG(issue_driven_score) as avg_issue_driven_score,
                        AVG(commit_issue_ratio) as avg_commit_issue_ratio,
                        AVG(issue_assignee_ratio) as avg_issue_assignee_ratio,
                        AVG(issue_closure_ratio) as avg_issue_closure_ratio
                    FROM project_statuses
                """)
                
                summary = await cur.fetchone()
                
                # 获取质量分布
                await cur.execute("""
                    SELECT 
                        issue_workflow_quality,
                        COUNT(*) as count
                    FROM project_statuses
                    GROUP BY issue_workflow_quality
                    ORDER BY count DESC
                """)
                
                quality_distribution = await cur.fetchall()
                
                return {
                    'summary': summary,
                    'quality_distribution': quality_distribution
                }
                
    except Exception as e:
        logger.error(f"获取同步摘要失败: {e}")
        return {}


def print_sync_summary(summary: Dict):
    """打印同步摘要"""
    if not summary or 'summary' not in summary:
        print("❌ 无法获取同步摘要")
        return
    
    summary_data = summary['summary']
    quality_dist = summary.get('quality_distribution', [])
    
    print(f"\n📊 Issue驱动开发数据同步摘要")
    print(f"=" * 50)
    print(f"总项目数: {summary_data['total_projects']}")
    print(f"使用Issue驱动开发: {summary_data['projects_with_issue_driven']} ({summary_data['projects_with_issue_driven']/summary_data['total_projects']*100:.1f}%)")
    print(f"平均评分: {summary_data['avg_issue_driven_score']:.1f}/100")
    print(f"平均提交-Issue关联率: {summary_data['avg_commit_issue_ratio']:.1f}%")
    print(f"平均Issue负责人分配率: {summary_data['avg_issue_assignee_ratio']:.1f}%")
    print(f"平均Issue关闭率: {summary_data['avg_issue_closure_ratio']:.1f}%")
    
    if quality_dist:
        print(f"\n工作流程质量分布:")
        for item in quality_dist:
            percentage = item['count'] / summary_data['total_projects'] * 100
            print(f"  {item['issue_workflow_quality']}: {item['count']}个项目 ({percentage:.1f}%)")


async def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="Issue驱动开发数据同步脚本")
    parser.add_argument("--analysis-file", default="issue_driven_analysis.json", 
                       help="分析结果文件路径")
    parser.add_argument("--summary-only", action="store_true", 
                       help="只显示同步摘要，不执行同步")
    parser.add_argument("--verbose", action="store_true", 
                       help="显示详细日志")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    print("🚀 开始Issue驱动开发数据同步...")
    
    if args.summary_only:
        # 只显示摘要
        summary = await get_sync_summary()
        print_sync_summary(summary)
        return 0
    
    # 执行同步
    success = await sync_issue_driven_data(args.analysis_file)
    
    if success:
        print("✅ 数据同步完成")
        
        # 显示同步摘要
        summary = await get_sync_summary()
        print_sync_summary(summary)
        
        return 0
    else:
        print("❌ 数据同步失败")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 