#!/usr/bin/env python3
"""
测试语言分析功能
"""

import asyncio
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backend'))

from app.language_analyzer import LanguageAnalyzer
from app.project_analyzer import ProjectAnalyzer


async def test_language_analysis():
    """测试语言分析功能"""
    print("🔍 开始测试语言分析功能...")
    
    # 测试语言分析器
    analyzer = LanguageAnalyzer()
    
    # 测试当前项目
    current_project = Path("/Users/mars/jobs/pq/edashboard")
    
    print(f"\n📁 分析项目: {current_project}")
    
    # 分析技术栈
    tech_stack = analyzer.analyze_project_tech_stack(current_project)
    
    print("\n📊 技术栈分析结果:")
    print("=" * 50)
    
    # 编程语言
    print("\n🔤 编程语言:")
    for lang, count in tech_stack['languages'].items():
        print(f"  {lang}: {count} 个文件")
    
    # 框架
    print("\n⚙️ 框架和库:")
    for framework, count in tech_stack['frameworks'].items():
        print(f"  {framework}: {count} 次使用")
    
    # AI技术
    print("\n🤖 AI技术:")
    ai_tech = tech_stack['ai_technologies']
    if ai_tech['models']:
        print("  AI模型:")
        for model in ai_tech['models']:
            print(f"    - {model}")
    
    if ai_tech['libraries']:
        print("  AI库:")
        for library in ai_tech['libraries']:
            print(f"    - {library}")
    
    if ai_tech['runtimes']:
        print("  AI运行时:")
        for runtime in ai_tech['runtimes']:
            print(f"    - {runtime}")
    
    # 摘要
    print("\n📋 技术栈摘要:")
    summary = tech_stack['summary']
    print(f"  主要语言: {summary.get('primary_language', 'Unknown')}")
    print(f"  语言种类: {summary.get('language_count', 0)}")
    print(f"  框架种类: {summary.get('framework_count', 0)}")
    print(f"  主要框架: {', '.join(summary.get('main_frameworks', []))}")
    print(f"  使用AI: {'是' if summary.get('has_ai', False) else '否'}")
    
    if summary.get('has_ai'):
        print(f"  AI模型: {', '.join(summary.get('ai_models', []))}")
        print(f"  AI库: {', '.join(summary.get('ai_libraries', []))}")


async def test_project_analyzer():
    """测试项目分析器"""
    print("\n🔍 开始测试项目分析器...")
    
    analyzer = ProjectAnalyzer()
    
    # 分析所有项目
    print("正在分析所有项目...")
    projects = await analyzer.analyze_all_projects()
    
    print(f"\n📊 找到 {len(projects)} 个项目")
    
    # 统计技术栈
    language_stats = {}
    framework_stats = {}
    ai_project_count = 0
    
    for project_key, project_data in projects.items():
        tech_stack = project_data.get('tech_stack', {})
        
        # 统计语言
        for lang, count in tech_stack.get('languages', {}).items():
            if lang not in language_stats:
                language_stats[lang] = {'count': 0, 'projects': []}
            language_stats[lang]['count'] += count
            if project_key not in language_stats[lang]['projects']:
                language_stats[lang]['projects'].append(project_key)
        
        # 统计框架
        for framework, count in tech_stack.get('frameworks', {}).items():
            if framework not in framework_stats:
                framework_stats[framework] = {'count': 0, 'projects': []}
            framework_stats[framework]['count'] += count
            if project_key not in framework_stats[framework]['projects']:
                framework_stats[framework]['projects'].append(project_key)
        
        # 统计AI项目
        if tech_stack.get('summary', {}).get('has_ai', False):
            ai_project_count += 1
    
    print(f"\n🔤 编程语言统计 (按项目数量排序):")
    sorted_languages = sorted(
        language_stats.items(), 
        key=lambda x: len(x[1]['projects']), 
        reverse=True
    )
    for lang, stats in sorted_languages[:10]:
        print(f"  {lang}: {len(stats['projects'])} 个项目, {stats['count']} 个文件")
    
    print(f"\n⚙️ 框架统计 (按项目数量排序):")
    sorted_frameworks = sorted(
        framework_stats.items(), 
        key=lambda x: len(x[1]['projects']), 
        reverse=True
    )
    for framework, stats in sorted_frameworks[:10]:
        print(f"  {framework}: {len(stats['projects'])} 个项目, {stats['count']} 次使用")
    
    print(f"\n🤖 AI项目统计:")
    print(f"  使用AI技术的项目: {ai_project_count}")
    print(f"  AI项目占比: {(ai_project_count / len(projects) * 100):.1f}%")


async def main():
    """主函数"""
    print("🚀 语言和框架分析测试")
    print("=" * 60)
    
    try:
        await test_language_analysis()
        await test_project_analyzer()
        
        print("\n✅ 测试完成!")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main()) 