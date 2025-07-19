#!/usr/bin/env python3
"""
生成项目总结报告

基于项目分析结果生成总体统计报告。
"""

import json
import argparse
from pathlib import Path
from datetime import datetime
from collections import defaultdict


def load_analysis_data(json_file: str) -> dict:
    """加载分析数据"""
    with open(json_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def generate_summary_report(data: dict) -> str:
    """生成总结报告"""
    report = []
    report.append("# 📊 项目状态总结报告")
    report.append("")
    report.append(f"*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
    report.append("")
    
    # 基本统计
    total_projects = len(data)
    report.append("## 📈 基本统计")
    report.append("")
    report.append(f"- **总项目数**: {total_projects}")
    report.append("")
    
    # README统计
    projects_with_readme = sum(1 for p in data.values() if p['structure']['has_readme'])
    projects_without_readme = total_projects - projects_with_readme
    readme_coverage = round(projects_with_readme / total_projects * 100, 1)
    
    report.append("## 📚 README文档统计")
    report.append("")
    report.append(f"- **包含README**: {projects_with_readme} 个项目 ({readme_coverage}%)")
    report.append(f"- **不包含README**: {projects_without_readme} 个项目 ({100-readme_coverage}%)")
    report.append("")
    
    # 编程语言统计
    languages = defaultdict(int)
    for project_data in data.values():
        lang = project_data['structure']['main_language']
        if lang:
            languages[lang] += 1
    
    if languages:
        report.append("## 💻 编程语言分布")
        report.append("")
        sorted_langs = sorted(languages.items(), key=lambda x: x[1], reverse=True)
        for lang, count in sorted_langs:
            percentage = round(count / total_projects * 100, 1)
            report.append(f"- **{lang}**: {count} 个项目 ({percentage}%)")
        report.append("")
    
    # 项目大小统计
    sizes = [p['structure']['project_size_kb'] for p in data.values()]
    avg_size = sum(sizes) / len(sizes) if sizes else 0
    max_size = max(sizes) if sizes else 0
    min_size = min(sizes) if sizes else 0
    
    report.append("## 📦 项目大小统计")
    report.append("")
    report.append(f"- **平均大小**: {avg_size:.1f} KB")
    report.append(f"- **最大项目**: {max_size:.1f} KB")
    report.append(f"- **最小项目**: {min_size:.1f} KB")
    report.append("")
    
    # 开发活跃度统计
    commit_counts = [p['git_info']['commit_count'] for p in data.values()]
    contributor_counts = [p['git_info']['contributors'] for p in data.values()]
    
    avg_commits = sum(commit_counts) / len(commit_counts) if commit_counts else 0
    avg_contributors = sum(contributor_counts) / len(contributor_counts) if contributor_counts else 0
    
    report.append("## 🔄 开发活跃度统计")
    report.append("")
    report.append(f"- **平均提交次数**: {avg_commits:.1f}")
    report.append(f"- **平均贡献者数**: {avg_contributors:.1f}")
    report.append("")
    
    # 项目配置统计
    configs = {
        'package.json': sum(1 for p in data.values() if p['structure']['has_package_json']),
        'requirements.txt': sum(1 for p in data.values() if p['structure']['has_requirements_txt']),
        'Docker配置': sum(1 for p in data.values() if p['structure']['has_dockerfile'])
    }
    
    report.append("## ⚙️ 项目配置统计")
    report.append("")
    for config, count in configs.items():
        percentage = round(count / total_projects * 100, 1)
        report.append(f"- **{config}**: {count} 个项目 ({percentage}%)")
    report.append("")
    
    # 项目评分统计
    scores = []
    for project_data in data.values():
        score = 0
        structure = project_data['structure']
        git_info = project_data['git_info']
        
        if structure['has_readme']:
            score += 25
        if structure['code_files'] > 0:
            score += 25
        if structure['has_package_json'] or structure['has_requirements_txt']:
            score += 25
        if git_info['commit_count'] > 0:
            score += 25
        
        scores.append(score)
    
    avg_score = sum(scores) / len(scores) if scores else 0
    excellent_projects = sum(1 for s in scores if s >= 75)
    good_projects = sum(1 for s in scores if 50 <= s < 75)
    poor_projects = sum(1 for s in scores if s < 50)
    
    report.append("## 🏆 项目质量评分")
    report.append("")
    report.append(f"- **平均评分**: {avg_score:.1f}/100")
    report.append(f"- **优秀项目** (≥75分): {excellent_projects} 个")
    report.append(f"- **良好项目** (50-74分): {good_projects} 个")
    report.append(f"- **待改进项目** (<50分): {poor_projects} 个")
    report.append("")
    
    # 详细项目列表
    report.append("## 📋 项目详细列表")
    report.append("")
    
    # 按评分排序
    project_scores = []
    for project_key, project_data in data.items():
        score = 0
        structure = project_data['structure']
        git_info = project_data['git_info']
        
        if structure['has_readme']:
            score += 25
        if structure['code_files'] > 0:
            score += 25
        if structure['has_package_json'] or structure['has_requirements_txt']:
            score += 25
        if git_info['commit_count'] > 0:
            score += 25
        
        project_scores.append((project_key, score, project_data))
    
    project_scores.sort(key=lambda x: x[1], reverse=True)
    
    for project_key, score, project_data in project_scores:
        structure = project_data['structure']
        git_info = project_data['git_info']
        
        status_emoji = "🟢" if score >= 75 else "🟡" if score >= 50 else "🔴"
        readme_status = "✅" if structure['has_readme'] else "❌"
        lang = structure['main_language'] or "未知"
        
        report.append(f"{status_emoji} **{project_key}** (评分: {score}/100)")
        report.append(f"   - 语言: {lang}")
        report.append(f"   - README: {readme_status}")
        report.append(f"   - 大小: {structure['project_size_kb']:.1f} KB")
        report.append(f"   - 提交: {git_info['commit_count']} 次")
        report.append(f"   - 贡献者: {git_info['contributors']} 人")
        report.append("")
    
    # 建议
    report.append("## 💡 总体建议")
    report.append("")
    
    if readme_coverage < 80:
        report.append("### 📚 README文档改进")
        report.append(f"- 当前README覆盖率: {readme_coverage}%")
        report.append("- 建议所有项目都添加README.md文档")
        report.append("- README应包含项目介绍、安装说明、使用方法等")
        report.append("")
    
    if avg_score < 70:
        report.append("### 🏗️ 项目结构改进")
        report.append("- 建议完善项目配置文件")
        report.append("- 确保代码文件结构清晰")
        report.append("- 添加必要的依赖管理文件")
        report.append("")
    
    if avg_commits < 5:
        report.append("### 🔄 开发活跃度")
        report.append("- 建议增加代码提交频率")
        report.append("- 鼓励团队协作开发")
        report.append("- 建立代码审查流程")
        report.append("")
    
    report.append("---")
    report.append("*此报告基于自动化分析生成，仅供参考*")
    
    return "\n".join(report)


def main():
    parser = argparse.ArgumentParser(
        description="生成项目总结报告",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python generate_summary_report.py project_analysis.json
  python generate_summary_report.py project_analysis.json --output summary.md
        """
    )
    
    parser.add_argument(
        'json_file',
        help='项目分析JSON文件'
    )
    
    parser.add_argument(
        '--output',
        help='输出文件路径'
    )
    
    args = parser.parse_args()
    
    # 加载数据
    data = load_analysis_data(args.json_file)
    
    # 生成报告
    report = generate_summary_report(data)
    
    # 输出
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"总结报告已保存到: {args.output}")
    else:
        print(report)


if __name__ == '__main__':
    main() 