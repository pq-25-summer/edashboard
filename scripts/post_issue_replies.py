#!/usr/bin/env python3
"""
使用GitHub CLI提交Issue #4的回复
"""

import requests
import json
import subprocess
import time

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

def post_comment(comment):
    """使用gh客户端提交评论"""
    try:
        # 将评论内容写入临时文件
        with open("temp_comment.md", "w", encoding="utf-8") as f:
            f.write(comment)
        
        # 使用gh客户端提交评论
        result = subprocess.run([
            "gh", "issue", "comment", "4", 
            "--body-file", "temp_comment.md",
            "--repo", "pq-25-summer/edashboard"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ 评论提交成功")
            return True
        else:
            print(f"❌ 评论提交失败: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ 提交评论时出错: {e}")
        return False
    finally:
        # 清理临时文件
        try:
            import os
            os.remove("temp_comment.md")
        except:
            pass

def main():
    """主函数"""
    print("=" * 60)
    print("使用GitHub CLI提交Issue #4回复")
    print("=" * 60)
    
    # 获取项目数据
    projects = get_project_data()
    
    if not projects:
        print("❌ 无法获取项目数据")
        return
    
    print(f"📊 找到 {len(projects)} 个项目")
    
    # 按覆盖率排序项目
    sorted_projects = sorted(projects, key=lambda x: float(x['test_coverage']), reverse=True)
    
    # 提交总体统计
    total_projects = len(projects)
    projects_with_unit_tests = sum(1 for p in projects if p['has_unit_tests'])
    projects_with_test_plan = sum(1 for p in projects if p['has_test_plan'])
    projects_with_test_docs = sum(1 for p in projects if p['has_test_documentation'])
    projects_using_tdd = sum(1 for p in projects if p['uses_tdd'])
    avg_coverage = sum(float(p['test_coverage']) for p in projects) / len(projects)
    
    summary_comment = f"""## 📊 总体统计

**分析时间**: 2025-07-20
**总项目数**: {total_projects}
**有单元测试的项目**: {projects_with_unit_tests} ({projects_with_unit_tests/total_projects*100:.1f}%)
**有测试方案的项目**: {projects_with_test_plan} ({projects_with_test_plan/total_projects*100:.1f}%)
**有测试文档的项目**: {projects_with_test_docs} ({projects_with_test_docs/total_projects*100:.1f}%)
**使用TDD的项目**: {projects_using_tdd} ({projects_using_tdd/total_projects*100:.1f}%)
**平均测试覆盖率**: {avg_coverage:.2f}%

---

"""
    
    print("📝 提交总体统计...")
    if post_comment(summary_comment):
        print("✅ 总体统计提交成功")
    else:
        print("❌ 总体统计提交失败")
        return
    
    # 等待一下避免API限制
    time.sleep(2)
    
    # 逐个提交项目回复
    for i, project in enumerate(sorted_projects, 1):
        project_name = project['project_name']
        print(f"📝 提交回复 {i}/{len(sorted_projects)}: {project_name}")
        
        comment = generate_reply(project)
        if post_comment(comment):
            print(f"✅ {project_name} 回复提交成功")
        else:
            print(f"❌ {project_name} 回复提交失败")
            break
        
        # 等待一下避免API限制
        time.sleep(1)
    
    print("=" * 60)
    print("🎉 所有回复提交完成！")
    print("=" * 60)

if __name__ == "__main__":
    main() 