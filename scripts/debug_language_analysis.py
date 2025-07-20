#!/usr/bin/env python3
"""
调试语言分析器
"""

import sys
import os
from pathlib import Path

# 添加backend目录到Python路径
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backend'))

from app.language_analyzer import LanguageAnalyzer


def test_language_analysis():
    """测试语言分析"""
    analyzer = LanguageAnalyzer()
    
    # 测试一个具体的项目
    test_repo = Path("/Users/mars/jobs/pq/repos/ldg-aqing/llj-public")
    
    print(f"🔍 测试项目: {test_repo}")
    print("=" * 50)
    
    # 分析语言
    print("📊 分析编程语言...")
    languages = analyzer.analyze_project_languages(test_repo)
    print(f"检测到的语言: {languages}")
    
    # 分析框架
    print("\n📊 分析框架和库...")
    frameworks = analyzer.analyze_project_frameworks(test_repo)
    print(f"检测到的框架: {frameworks}")
    
    # 分析AI技术
    print("\n📊 分析AI技术...")
    ai_tech = analyzer.analyze_ai_technologies(test_repo)
    print(f"检测到的AI技术: {ai_tech}")
    
    # 综合分析
    print("\n📊 综合分析技术栈...")
    tech_stack = analyzer.analyze_project_tech_stack(test_repo)
    print(f"技术栈分析结果:")
    print(f"  - 语言: {tech_stack['languages']}")
    print(f"  - 框架: {tech_stack['frameworks']}")
    print(f"  - AI技术: {tech_stack['ai_technologies']}")
    print(f"  - 摘要: {tech_stack['summary']}")


if __name__ == "__main__":
    test_language_analysis() 