#!/usr/bin/env python3
"""
更新项目状态数据库，包含Git工作流程分析结果
"""

import os
import sys
import asyncio
from pathlib import Path
from typing import Dict, List, Optional

# 设置环境变量（必须在导入模块之前）
os.environ['LOCAL_REPOS_DIR'] = '/Users/mars/jobs/pq/repos'
os.environ['DATABASE_URL'] = 'postgresql://localhost/edashboard'
os.environ['GITHUB_API_BASE_URL'] = 'https://api.github.com'
os.environ['APP_NAME'] = '软件工程课看板系统'
os.environ['DEBUG'] = 'true'
os.environ['SECRET_KEY'] = 'your-secret-key-here-change-in-production'
os.environ['ALGORITHM'] = 'HS256'
os.environ['ACCESS_TOKEN_EXPIRE_MINUTES'] = '30'

# 添加backend目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.project_analyzer import ProjectAnalyzer
from app.database import db


async def update_project_status_with_git_workflow():
    """更新项目状态，包含Git工作流程分析"""
    print("🚀 开始更新项目状态（包含Git工作流程分析）...")
    
    try:
        # 创建项目分析器
        analyzer = ProjectAnalyzer()
        
        # 分析所有项目
        print("🔍 分析所有项目...")
        results = await analyzer.analyze_all_projects()
        
        if not results:
            print("❌ 没有找到任何项目")
            return
        
        print(f"📊 找到 {len(results)} 个项目")
        
        # 更新数据库
        async with db.get_db() as conn:
            updated_count = 0
            
            for project_key, analysis in results.items():
                try:
                    # 从项目路径提取owner/repo
                    parts = project_key.split('/')
                    if len(parts) >= 2:
                        owner = parts[0]
                        repo = parts[1]
                        
                        # 查找项目ID
                        async with conn.cursor() as cur:
                            await cur.execute("""
                                SELECT id FROM projects 
                                WHERE github_url LIKE %s
                            """, (f"%{owner}/{repo}%",))
                            
                            project_result = await cur.fetchone()
                            
                            if project_result:
                                project_id = project_result['id']
                                
                                # 获取工作流程信息
                                workflow_info = analysis.get('workflow_info', {})
                                
                                # 更新项目状态
                                await cur.execute("""
                                    INSERT INTO project_statuses (
                                        project_id, has_readme, readme_files, total_files,
                                        code_files, doc_files, config_files, project_size_kb,
                                        main_language, commit_count, contributors, last_commit,
                                        current_branch, has_package_json, has_requirements_txt,
                                        has_dockerfile, quality_score, workflow_style, workflow_score,
                                        total_branches, feature_branches, hotfix_branches,
                                        merge_commits, rebase_commits, uses_feature_branches,
                                        uses_main_branch_merges, uses_rebase, uses_pull_requests,
                                        updated_at
                                    ) VALUES (
                                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP
                                    )
                                    ON CONFLICT (project_id) DO UPDATE SET
                                        has_readme = EXCLUDED.has_readme,
                                        readme_files = EXCLUDED.readme_files,
                                        total_files = EXCLUDED.total_files,
                                        code_files = EXCLUDED.code_files,
                                        doc_files = EXCLUDED.doc_files,
                                        config_files = EXCLUDED.config_files,
                                        project_size_kb = EXCLUDED.project_size_kb,
                                        main_language = EXCLUDED.main_language,
                                        commit_count = EXCLUDED.commit_count,
                                        contributors = EXCLUDED.contributors,
                                        last_commit = EXCLUDED.last_commit,
                                        current_branch = EXCLUDED.current_branch,
                                        has_package_json = EXCLUDED.has_package_json,
                                        has_requirements_txt = EXCLUDED.has_requirements_txt,
                                        has_dockerfile = EXCLUDED.has_dockerfile,
                                        quality_score = EXCLUDED.quality_score,
                                        workflow_style = EXCLUDED.workflow_style,
                                        workflow_score = EXCLUDED.workflow_score,
                                        total_branches = EXCLUDED.total_branches,
                                        feature_branches = EXCLUDED.feature_branches,
                                        hotfix_branches = EXCLUDED.hotfix_branches,
                                        merge_commits = EXCLUDED.merge_commits,
                                        rebase_commits = EXCLUDED.rebase_commits,
                                        uses_feature_branches = EXCLUDED.uses_feature_branches,
                                        uses_main_branch_merges = EXCLUDED.uses_main_branch_merges,
                                        uses_rebase = EXCLUDED.uses_rebase,
                                        uses_pull_requests = EXCLUDED.uses_pull_requests,
                                        updated_at = CURRENT_TIMESTAMP
                                """, (
                                    project_id,
                                    analysis['structure']['has_readme'],
                                    analysis['structure']['readme_files'],
                                    analysis['structure']['total_files'],
                                    analysis['structure']['code_files'],
                                    analysis['structure']['doc_files'],
                                    analysis['structure']['config_files'],
                                    analysis['structure']['project_size_kb'],
                                    analysis['structure']['main_language'],
                                    analysis['git_info']['commit_count'],
                                    analysis['git_info']['contributors'],
                                    analysis['git_info']['last_commit'],
                                    analysis['git_info']['branch'],
                                    analysis['structure']['has_package_json'],
                                    analysis['structure']['has_requirements_txt'],
                                    analysis['structure']['has_dockerfile'],
                                    analysis['quality_score'],
                                    workflow_info.get('workflow_style'),
                                    workflow_info.get('workflow_score', 0.0),
                                    workflow_info.get('total_branches', 0),
                                    workflow_info.get('feature_branches', 0),
                                    workflow_info.get('hotfix_branches', 0),
                                    workflow_info.get('merge_commits', 0),
                                    workflow_info.get('rebase_commits', 0),
                                    workflow_info.get('uses_feature_branches', False),
                                    workflow_info.get('uses_main_branch_merges', False),
                                    workflow_info.get('uses_rebase', False),
                                    workflow_info.get('uses_pull_requests', False)
                                ))
                                
                                updated_count += 1
                                print(f"✅ 更新项目状态: {project_key}")
                            else:
                                print(f"⚠️ 未找到项目: {project_key}")
                
                except Exception as e:
                    print(f"❌ 更新项目状态失败 {project_key}: {e}")
            
            await conn.commit()
            print(f"\n📊 成功更新 {updated_count} 个项目状态")
        
    except Exception as e:
        print(f"❌ 更新项目状态时出错: {e}")
        import traceback
        traceback.print_exc()


def main():
    """主函数"""
    # 运行更新
    asyncio.run(update_project_status_with_git_workflow())


if __name__ == "__main__":
    main() 