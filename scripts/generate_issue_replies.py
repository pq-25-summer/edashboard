#!/usr/bin/env python3
"""
生成Issue #4的回复内容
为每个项目生成一条测试情况统计回复
"""

import requests
import json

def get_project_data():
    """获取项目测试数据"""
    try:
        response = requests.get("http://localhost:8000/api/test-analysis/projects")
        if response.status_code == 200:
            return response.json()
        else:
            print(f"获取数据失败: {response.status_code}")
            return []
    except Exception as e:
        print(f"请求失败: {e}")
        return []

def generate_reply(project):
    """为单个项目生成回复内容"""
    project_name = project['project_name']
    has_unit_tests = project['has_unit_tests']
    has_test_plan = project['has_test_plan']
    has_test_documentation = project['has_test_documentation']
    uses_tdd = project['uses_tdd']
    test_coverage = float(project['test_coverage'])
    test_frameworks = project['test_frameworks']
    
    # 生成状态图标
    unit_test_status = "✅" if has_unit_tests else "❌"
    test_plan_status = "✅" if has_test_plan else "❌"
    test_doc_status = "✅" if has_test_documentation else "❌"
    tdd_status = "✅" if uses_tdd else "❌"
    
    # 生成覆盖率颜色
    if test_coverage >= 75:
        coverage_color = "🟢"
    elif test_coverage >= 50:
        coverage_color = "🟡"
    elif test_coverage >= 25:
        coverage_color = "🟠"
    else:
        coverage_color = "🔴"
    
    # 生成框架信息
    if test_frameworks:
        frameworks_text = f"测试框架: {', '.join(test_frameworks)}"
    else:
        frameworks_text = "测试框架: 未检测到"
    
    reply = f"""## 📁 项目: {project_name}

**测试情况统计:**

- **单元测试**: {unit_test_status} {'有' if has_unit_tests else '无'}
- **测试方案**: {test_plan_status} {'有' if has_test_plan else '无'}
- **测试文档**: {test_doc_status} {'有' if has_test_documentation else '无'}
- **TDD实践**: {tdd_status} {'使用' if uses_tdd else '未使用'}
- **测试覆盖率**: {coverage_color} {test_coverage}%
- **{frameworks_text}**

---
"""
    return reply

def main():
    """主函数"""
    print("=" * 60)
    print("生成Issue #4回复内容")
    print("=" * 60)
    
    # 获取项目数据
    projects = get_project_data()
    
    if not projects:
        print("❌ 无法获取项目数据")
        return
    
    print(f"📊 找到 {len(projects)} 个项目")
    print("\n" + "=" * 60)
    print("回复内容 (请复制到Issue #4):")
    print("=" * 60)
    
    # 生成总体统计
    total_projects = len(projects)
    projects_with_unit_tests = sum(1 for p in projects if p['has_unit_tests'])
    projects_with_test_plan = sum(1 for p in projects if p['has_test_plan'])
    projects_with_test_docs = sum(1 for p in projects if p['has_test_documentation'])
    projects_using_tdd = sum(1 for p in projects if p['uses_tdd'])
    avg_coverage = sum(float(p['test_coverage']) for p in projects) / len(projects)
    
    print(f"""## 📊 总体统计

**分析时间**: 2025-07-20
**总项目数**: {total_projects}
**有单元测试的项目**: {projects_with_unit_tests} ({projects_with_unit_tests/total_projects*100:.1f}%)
**有测试方案的项目**: {projects_with_test_plan} ({projects_with_test_plan/total_projects*100:.1f}%)
**有测试文档的项目**: {projects_with_test_docs} ({projects_with_test_docs/total_projects*100:.1f}%)
**使用TDD的项目**: {projects_using_tdd} ({projects_using_tdd/total_projects*100:.1f}%)
**平均测试覆盖率**: {avg_coverage:.2f}%

---

""")
    
    # 按覆盖率排序项目
    sorted_projects = sorted(projects, key=lambda x: x['test_coverage'], reverse=True)
    
    # 生成每个项目的回复
    for i, project in enumerate(sorted_projects, 1):
        print(f"### 回复 {i}: {project['project_name']}")
        print(generate_reply(project))
    
    print("=" * 60)
    print("✅ 回复内容生成完成！")
    print("请将上述内容复制到Issue #4中，每个项目一条回复。")
    print("=" * 60)

if __name__ == "__main__":
    main() 