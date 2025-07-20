#!/usr/bin/env python3
"""
保存技术栈数据到数据库
"""

import asyncio
import sys
import os
import json
from datetime import datetime

# 添加backend目录到Python路径
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backend'))

from app.database import db, init_db
from app.language_analyzer import LanguageAnalyzer
from app.project_analyzer import ProjectAnalyzer


async def create_tech_stack_tables():
    """创建技术栈相关的数据库表"""
    async with db.get_db() as conn:
        # 创建项目技术栈表
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS project_tech_stacks (
                id SERIAL PRIMARY KEY,
                project_id INTEGER REFERENCES projects(id) UNIQUE,
                languages JSONB,
                frameworks JSONB,
                ai_models JSONB,
                ai_libraries JSONB,
                ai_runtimes JSONB,
                total_languages INTEGER DEFAULT 0,
                total_frameworks INTEGER DEFAULT 0,
                total_ai_models INTEGER DEFAULT 0,
                total_ai_libraries INTEGER DEFAULT 0,
                has_ai BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 创建技术栈统计表
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS tech_stack_statistics (
                id SERIAL PRIMARY KEY,
                language_summary JSONB,
                framework_summary JSONB,
                ai_summary JSONB,
                total_projects INTEGER DEFAULT 0,
                analysis_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        await conn.commit()
        print("✅ 技术栈表创建完成")


async def save_project_tech_stacks():
    """保存项目技术栈数据"""
    analyzer = ProjectAnalyzer()
    language_analyzer = LanguageAnalyzer()
    
    print("🔍 开始分析项目技术栈...")
    
    # 分析所有项目
    results = await analyzer.analyze_all_projects()
    
    async with db.get_db() as conn:
        for project_key, project_data in results.items():
            try:
                # 查找项目ID
                async with conn.cursor() as cur:
                    # 从project_key构建GitHub URL格式
                    if '/' in project_key:
                        owner, repo = project_key.split('/', 1)
                        github_url = f"https://github.com/{owner}/{repo}"
                        
                        await cur.execute(
                            "SELECT id FROM projects WHERE github_url = %s",
                            (github_url,)
                        )
                        project_result = await cur.fetchone()
                        
                        if not project_result:
                            print(f"⚠️  未找到项目: {project_key} (URL: {github_url})")
                            continue
                        
                        project_id = project_result["id"]
                        print(f"✅ 找到项目: {project_key} -> ID: {project_id}")
                    else:
                        print(f"⚠️  无效的项目键: {project_key}")
                        continue
                    
                    # 分析技术栈
                    repo_path = project_data.get('path', '')
                    if repo_path and os.path.exists(repo_path):
                        try:
                            # 检查项目分析器是否已经分析了技术栈
                            if 'tech_stack' in project_data:
                                tech_stack = project_data['tech_stack']
                                print(f"🔍 使用项目分析器已有的技术栈数据")
                            else:
                                tech_stack = language_analyzer.analyze_project_tech_stack(repo_path)
                                print(f"🔍 重新分析项目技术栈")
                            
                            # 打印调试信息
                            print(f"🔍 项目 {project_key} 技术栈分析结果:")
                            print(f"  - 语言: {tech_stack['languages']}")
                            print(f"  - 框架: {tech_stack['frameworks']}")
                            print(f"  - AI技术: {tech_stack['ai_technologies']}")
                            
                            # 保存技术栈数据
                            await cur.execute("""
                                INSERT INTO project_tech_stacks (
                                    project_id, languages, frameworks, ai_models, 
                                    ai_libraries, ai_runtimes, total_languages,
                                    total_frameworks, total_ai_models, total_ai_libraries,
                                    has_ai, updated_at
                                ) VALUES (
                                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW()
                                ) ON CONFLICT (project_id) DO UPDATE SET
                                    languages = EXCLUDED.languages,
                                    frameworks = EXCLUDED.frameworks,
                                    ai_models = EXCLUDED.ai_models,
                                    ai_libraries = EXCLUDED.ai_libraries,
                                    ai_runtimes = EXCLUDED.ai_runtimes,
                                    total_languages = EXCLUDED.total_languages,
                                    total_frameworks = EXCLUDED.total_frameworks,
                                    total_ai_models = EXCLUDED.total_ai_models,
                                    total_ai_libraries = EXCLUDED.total_ai_libraries,
                                    has_ai = EXCLUDED.has_ai,
                                    updated_at = NOW()
                            """, (
                                project_id,
                                json.dumps(tech_stack['languages']),
                                json.dumps(tech_stack['frameworks']),
                                json.dumps(tech_stack['ai_technologies']['models']),
                                json.dumps(tech_stack['ai_technologies']['libraries']),
                                json.dumps(tech_stack['ai_technologies']['runtimes']),
                                len(tech_stack['languages']),
                                len(tech_stack['frameworks']),
                                len(tech_stack['ai_technologies']['models']),
                                len(tech_stack['ai_technologies']['libraries']),
                                len(tech_stack['ai_technologies']['models']) > 0 or len(tech_stack['ai_technologies']['libraries']) > 0
                            ))
                            
                            print(f"✅ 已保存项目技术栈: {project_key}")
                        except Exception as e:
                            print(f"❌ 分析项目技术栈失败 {project_key}: {e}")
                            import traceback
                            traceback.print_exc()
                    else:
                        print(f"⚠️  项目路径不存在: {repo_path}")
                    
            except Exception as e:
                print(f"❌ 保存项目技术栈失败 {project_key}: {e}")
        
        await conn.commit()


async def save_tech_stack_statistics():
    """保存技术栈统计数据"""
    print("📊 生成技术栈统计数据...")
    
    async with db.get_db() as conn:
        async with conn.cursor() as cur:
            # 获取所有项目技术栈数据
            await cur.execute("""
                SELECT languages, frameworks, ai_models, ai_libraries, has_ai
                FROM project_tech_stacks
            """)
            results = await cur.fetchall()
            
            # 统计语言使用情况
            language_summary = {}
            framework_summary = {}
            ai_models_summary = {}
            ai_libraries_summary = {}
            projects_with_ai = 0
            
            for row in results:
                # 统计语言
                if row['languages']:
                    try:
                        languages = json.loads(row['languages']) if isinstance(row['languages'], str) else row['languages']
                        for lang, count in languages.items():
                            language_summary[lang] = language_summary.get(lang, 0) + 1
                    except:
                        pass
                
                # 统计框架
                if row['frameworks']:
                    try:
                        frameworks = json.loads(row['frameworks']) if isinstance(row['frameworks'], str) else row['frameworks']
                        for framework, count in frameworks.items():
                            framework_summary[framework] = framework_summary.get(framework, 0) + 1
                    except:
                        pass
                
                # 统计AI模型
                if row['ai_models']:
                    try:
                        ai_models = json.loads(row['ai_models']) if isinstance(row['ai_models'], str) else row['ai_models']
                        for model in ai_models:
                            ai_models_summary[model] = ai_models_summary.get(model, 0) + 1
                    except:
                        pass
                
                # 统计AI库
                if row['ai_libraries']:
                    try:
                        ai_libraries = json.loads(row['ai_libraries']) if isinstance(row['ai_libraries'], str) else row['ai_libraries']
                        for library in ai_libraries:
                            ai_libraries_summary[library] = ai_libraries_summary.get(library, 0) + 1
                    except:
                        pass
                
                # 统计AI项目
                if row['has_ai']:
                    projects_with_ai += 1
            
            # 保存统计数据
            await cur.execute("""
                INSERT INTO tech_stack_statistics (
                    language_summary, framework_summary, ai_summary, total_projects, analysis_time
                ) VALUES (
                    %s, %s, %s, %s, NOW()
                )
            """, (
                json.dumps(language_summary),
                json.dumps(framework_summary),
                json.dumps({
                    'ai_models': ai_models_summary,
                    'ai_libraries': ai_libraries_summary,
                    'projects_with_ai': projects_with_ai
                }),
                len(results)
            ))
            
            await conn.commit()
            
            print(f"✅ 技术栈统计完成:")
            print(f"   - 总项目数: {len(results)}")
            print(f"   - 语言种类: {len(language_summary)}")
            print(f"   - 框架种类: {len(framework_summary)}")
            print(f"   - AI项目数: {projects_with_ai}")
            print(f"   - AI模型种类: {len(ai_models_summary)}")
            print(f"   - AI库种类: {len(ai_libraries_summary)}")


async def main():
    """主函数"""
    print("=" * 60)
    print("💾 技术栈数据保存任务")
    print("=" * 60)
    
    try:
        # 初始化数据库
        await init_db()
        
        # 创建技术栈表
        await create_tech_stack_tables()
        
        # 保存项目技术栈
        await save_project_tech_stacks()
        
        # 保存统计数据
        await save_tech_stack_statistics()
        
        print("\n🎉 技术栈数据保存完成!")
        
    except Exception as e:
        print(f"❌ 技术栈数据保存失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main()) 