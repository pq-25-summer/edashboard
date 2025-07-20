"""
测试分析API路由
提供项目测试情况分析的API端点
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, List, Optional
import asyncio

from app.test_analyzer import TestAnalyzer
from app.database import db
from app.models import ProjectTestAnalysis, TestAnalysisSummary

router = APIRouter(prefix="/test-analysis", tags=["测试分析"])

# 创建测试分析器实例
test_analyzer = TestAnalyzer()


@router.post("/analyze-all", response_model=Dict[str, Dict])
async def analyze_all_projects_testing():
    """
    分析所有项目的测试情况
    
    返回每个项目的测试分析结果，包括：
    - 是否有单元测试
    - 是否有测试方案
    - 是否有测试文档
    - 是否使用测试驱动开发
    - 测试覆盖率等指标
    """
    try:
        results = await test_analyzer.analyze_all_projects_testing()
        
        # 保存分析结果到数据库
        await test_analyzer.save_test_analysis_to_db(results)
        
        return {
            "success": True,
            "message": f"成功分析 {len(results)} 个项目的测试情况",
            "data": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"分析失败: {str(e)}")


@router.get("/summary", response_model=TestAnalysisSummary)
async def get_test_analysis_summary():
    """
    获取测试分析摘要
    
    返回所有项目的测试情况统计信息
    """
    try:
        summary = await test_analyzer.get_test_analysis_summary()
        
        # 确保返回的数据结构符合模型要求
        if not summary:
            summary = {
                'summary': {
                    'total_projects': 0,
                    'projects_with_unit_tests': 0,
                    'projects_with_test_plan': 0,
                    'projects_with_test_docs': 0,
                    'projects_using_tdd': 0,
                    'avg_test_coverage': 0.0
                },
                'framework_distribution': [],
                'coverage_distribution': []
            }
        
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取摘要失败: {str(e)}")


@router.get("/projects/{project_name}", response_model=Dict)
async def get_project_test_analysis(project_name: str):
    """
    获取指定项目的测试分析结果
    
    Args:
        project_name: 项目名称（相对路径）
    """
    try:
        async with db.get_db() as conn:
            result = await conn.execute("""
                SELECT * FROM project_test_analysis 
                WHERE project_name = %s
            """, project_name)
            result = await result.fetchone()
            
            if not result:
                raise HTTPException(status_code=404, detail=f"项目 {project_name} 的测试分析结果不存在")
            
            return dict(result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取项目测试分析失败: {str(e)}")


@router.get("/projects", response_model=List[Dict])
async def get_all_projects_test_analysis():
    """
    获取所有项目的测试分析结果列表
    """
    try:
        async with db.get_db() as conn:
            results = await conn.execute("""
                SELECT * FROM project_test_analysis 
                ORDER BY project_name
            """)
            results = await results.fetchall()
            
            return [dict(row) for row in results]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取项目列表失败: {str(e)}")


@router.get("/statistics", response_model=Dict)
async def get_test_statistics():
    """
    获取测试统计信息
    
    返回详细的测试统计信息，包括：
    - 各项目的测试情况对比
    - 测试框架使用情况
    - 测试覆盖率分布
    - 最佳实践采用情况
    """
    try:
        summary = await test_analyzer.get_test_analysis_summary()
        
        # 计算额外的统计信息
        async with db.get_db() as conn:
            # 获取测试覆盖率最高的项目
            top_coverage_result = await conn.execute("""
                SELECT project_name, test_coverage 
                FROM project_test_analysis 
                WHERE test_coverage > 0 
                ORDER BY test_coverage DESC 
                LIMIT 5
            """)
            top_coverage = await top_coverage_result.fetchall()
            
            # 获取使用TDD的项目
            tdd_projects_result = await conn.execute("""
                SELECT project_name 
                FROM project_test_analysis 
                WHERE uses_tdd = true
            """)
            tdd_projects = await tdd_projects_result.fetchall()
            
            # 获取有完整测试的项目（有单元测试、测试方案、测试文档）
            complete_testing_result = await conn.execute("""
                SELECT project_name 
                FROM project_test_analysis 
                WHERE has_unit_tests = true 
                AND has_test_plan = true 
                AND has_test_documentation = true
            """)
            complete_testing = await complete_testing_result.fetchall()
        
        return {
            "summary": summary,
            "top_coverage_projects": [dict(row) for row in top_coverage],
            "tdd_projects": [row['project_name'] for row in tdd_projects],
            "complete_testing_projects": [row['project_name'] for row in complete_testing],
            "statistics": {
                "tdd_adoption_rate": len(tdd_projects) / max(summary['summary'].get('total_projects', 1), 1) * 100,
                "complete_testing_rate": len(complete_testing) / max(summary['summary'].get('total_projects', 1), 1) * 100
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取统计信息失败: {str(e)}")


@router.post("/refresh/{project_name}")
async def refresh_project_test_analysis(project_name: str):
    """
    刷新指定项目的测试分析结果
    
    Args:
        project_name: 项目名称（相对路径）
    """
    try:
        # 重新分析指定项目
        repos_dir = test_analyzer.repos_dir
        project_path = repos_dir / project_name
        
        if not project_path.exists():
            raise HTTPException(status_code=404, detail=f"项目路径不存在: {project_name}")
        
        # 分析项目
        analysis = await test_analyzer.analyze_project_testing(project_path)
        
        # 保存到数据库
        await test_analyzer.save_test_analysis_to_db({project_name: analysis})
        
        return {
            "success": True,
            "message": f"成功刷新项目 {project_name} 的测试分析结果",
            "data": analysis
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"刷新分析失败: {str(e)}")


@router.delete("/projects/{project_name}")
async def delete_project_test_analysis(project_name: str):
    """
    删除指定项目的测试分析结果
    
    Args:
        project_name: 项目名称（相对路径）
    """
    try:
        async with db.get_db() as conn:
            result = await conn.execute("""
                DELETE FROM project_test_analysis 
                WHERE project_name = %s
            """, project_name)
            
            return {
                "success": True,
                "message": f"成功删除项目 {project_name} 的测试分析结果"
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除失败: {str(e)}") 