#!/usr/bin/env python3
"""
测试分析脚本
实现Issue #4的需求：统计各项目的测试情况

分析内容包括：
- 是否有单元测试
- 是否有测试方案
- 是否有对应的文档
- 是否使用测试驱动开发
"""

import asyncio
import sys
import os
from pathlib import Path

# 添加backend目录到Python路径
backend_dir = Path(__file__).parent.parent / 'backend'
sys.path.insert(0, str(backend_dir))

from app.test_analyzer import TestAnalyzer
import json
from datetime import datetime


async def main():
    """主函数"""
    print("=" * 60)
    print("项目测试情况分析")
    print("实现Issue #4: 统计各项目的测试情况")
    print("=" * 60)
    
    # 创建测试分析器
    analyzer = TestAnalyzer()
    
    try:
        # 分析所有项目的测试情况
        print("\n开始分析所有项目的测试情况...")
        results = await analyzer.analyze_all_projects_testing()
        
        if not results:
            print("❌ 没有找到任何项目或分析失败")
            return
        
        print(f"✅ 成功分析 {len(results)} 个项目")
        
        # 保存分析结果到数据库
        print("\n保存分析结果到数据库...")
        await analyzer.save_test_analysis_to_db(results)
        print("✅ 分析结果已保存到数据库")
        
        # 获取摘要统计
        print("\n获取分析摘要...")
        summary = await analyzer.get_test_analysis_summary()
        
        # 打印分析结果
        print("\n" + "=" * 60)
        print("测试分析结果摘要")
        print("=" * 60)
        
        if summary and 'summary' in summary:
            stats = summary['summary']
            print(f"📊 总项目数: {stats.get('total_projects', 0)}")
            print(f"🧪 有单元测试的项目: {stats.get('projects_with_unit_tests', 0)}")
            print(f"📋 有测试方案的项目: {stats.get('projects_with_test_plan', 0)}")
            print(f"📚 有测试文档的项目: {stats.get('projects_with_test_docs', 0)}")
            print(f"🔄 使用TDD的项目: {stats.get('projects_using_tdd', 0)}")
            print(f"📈 平均测试覆盖率: {stats.get('avg_test_coverage', 0):.2f}%")
        
        # 打印测试框架分布
        if summary and 'framework_distribution' in summary:
            print("\n📊 测试框架使用情况:")
            for framework in summary['framework_distribution']:
                print(f"  - {framework['framework']}: {framework['project_count']} 个项目")
        
        # 打印覆盖率分布
        if summary and 'coverage_distribution' in summary:
            print("\n📈 测试覆盖率分布:")
            for coverage in summary['coverage_distribution']:
                print(f"  - {coverage['coverage_level']}: {coverage['project_count']} 个项目")
        
        # 打印详细结果
        print("\n" + "=" * 60)
        print("各项目详细测试情况")
        print("=" * 60)
        
        for project_name, analysis in results.items():
            print(f"\n📁 项目: {project_name}")
            print(f"  ├─ 单元测试: {'✅' if analysis['has_unit_tests'] else '❌'}")
            print(f"  ├─ 测试方案: {'✅' if analysis['has_test_plan'] else '❌'}")
            print(f"  ├─ 测试文档: {'✅' if analysis['has_test_documentation'] else '❌'}")
            print(f"  ├─ TDD实践: {'✅' if analysis['uses_tdd'] else '❌'}")
            print(f"  ├─ 测试覆盖率: {analysis['test_coverage']}%")
            print(f"  ├─ 测试文件数: {analysis['test_metrics'].get('total_test_files', 0)}")
            print(f"  ├─ 测试函数数: {analysis['test_metrics'].get('total_test_functions', 0)}")
            
            if analysis['test_frameworks']:
                print(f"  └─ 测试框架: {', '.join(analysis['test_frameworks'])}")
            else:
                print(f"  └─ 测试框架: 未检测到")
        
        # 生成报告文件
        report_file = Path(__file__).parent.parent / 'docs' / 'test_analysis_report.json'
        report_file.parent.mkdir(exist_ok=True)
        
        report_data = {
            'analysis_time': datetime.now().isoformat(),
            'total_projects': len(results),
            'summary': summary,
            'detailed_results': results
        }
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n📄 详细报告已保存到: {report_file}")
        
        # 生成Markdown报告
        markdown_file = Path(__file__).parent.parent / 'docs' / 'test_analysis_report.md'
        generate_markdown_report(report_data, markdown_file)
        print(f"📄 Markdown报告已保存到: {markdown_file}")
        
        print("\n" + "=" * 60)
        print("✅ 测试分析完成！")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ 分析过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


def generate_markdown_report(data, output_file):
    """生成Markdown格式的报告"""
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# 项目测试情况分析报告\n\n")
        f.write(f"**分析时间**: {data['analysis_time']}\n\n")
        f.write(f"**总项目数**: {data['total_projects']}\n\n")
        
        # 摘要统计
        if data['summary'] and 'summary' in data['summary']:
            stats = data['summary']['summary']
            f.write("## 摘要统计\n\n")
            f.write("| 指标 | 数值 |\n")
            f.write("|------|------|\n")
            f.write(f"| 总项目数 | {stats.get('total_projects', 0)} |\n")
            f.write(f"| 有单元测试的项目 | {stats.get('projects_with_unit_tests', 0)} |\n")
            f.write(f"| 有测试方案的项目 | {stats.get('projects_with_test_plan', 0)} |\n")
            f.write(f"| 有测试文档的项目 | {stats.get('projects_with_test_docs', 0)} |\n")
            f.write(f"| 使用TDD的项目 | {stats.get('projects_using_tdd', 0)} |\n")
            f.write(f"| 平均测试覆盖率 | {stats.get('avg_test_coverage', 0):.2f}% |\n\n")
        
        # 测试框架分布
        if data['summary'] and 'framework_distribution' in data['summary']:
            f.write("## 测试框架使用情况\n\n")
            f.write("| 框架 | 项目数 |\n")
            f.write("|------|--------|\n")
            for framework in data['summary']['framework_distribution']:
                f.write(f"| {framework['framework']} | {framework['project_count']} |\n")
            f.write("\n")
        
        # 覆盖率分布
        if data['summary'] and 'coverage_distribution' in data['summary']:
            f.write("## 测试覆盖率分布\n\n")
            f.write("| 覆盖率级别 | 项目数 |\n")
            f.write("|------------|--------|\n")
            for coverage in data['summary']['coverage_distribution']:
                f.write(f"| {coverage['coverage_level']} | {coverage['project_count']} |\n")
            f.write("\n")
        
        # 详细结果
        f.write("## 各项目详细测试情况\n\n")
        f.write("| 项目名称 | 单元测试 | 测试方案 | 测试文档 | TDD实践 | 测试覆盖率 | 测试文件数 | 测试函数数 | 测试框架 |\n")
        f.write("|----------|----------|----------|----------|---------|------------|------------|------------|----------|\n")
        
        for project_name, analysis in data['detailed_results'].items():
            unit_tests = "✅" if analysis['has_unit_tests'] else "❌"
            test_plan = "✅" if analysis['has_test_plan'] else "❌"
            test_docs = "✅" if analysis['has_test_documentation'] else "❌"
            tdd = "✅" if analysis['uses_tdd'] else "❌"
            coverage = f"{analysis['test_coverage']}%"
            test_files = analysis['test_metrics'].get('total_test_files', 0)
            test_functions = analysis['test_metrics'].get('total_test_functions', 0)
            frameworks = ", ".join(analysis['test_frameworks']) if analysis['test_frameworks'] else "无"
            
            f.write(f"| {project_name} | {unit_tests} | {test_plan} | {test_docs} | {tdd} | {coverage} | {test_files} | {test_functions} | {frameworks} |\n")


if __name__ == "__main__":
    asyncio.run(main()) 