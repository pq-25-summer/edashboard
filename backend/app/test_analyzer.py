"""
测试分析模块
用于分析项目的测试情况，实现Issue #4的需求
"""

import os
import re
import subprocess
import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

from app.config import settings
from app.database import db


class TestAnalyzer:
    def __init__(self):
        self.repos_dir = Path(settings.local_repos_dir)
        self.setup_logging()
    
    def setup_logging(self):
        """设置日志"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    async def analyze_all_projects_testing(self) -> Dict[str, Dict]:
        """分析所有项目的测试情况"""
        if not self.repos_dir.exists():
            self.logger.error(f"本地仓库目录不存在: {self.repos_dir}")
            return {}
        
        git_repos = []
        try:
            for git_dir in self.repos_dir.rglob('.git'):
                if git_dir.is_dir():
                    project_dir = git_dir.parent
                    git_repos.append(project_dir)
        except Exception as e:
            self.logger.error(f"查找Git仓库失败: {e}")
            return {}
        
        self.logger.info(f"找到 {len(git_repos)} 个Git仓库，开始分析测试情况")
        
        results = {}
        for repo_path in git_repos:
            relative_path = repo_path.relative_to(self.repos_dir)
            project_key = str(relative_path)
            
            self.logger.info(f"分析项目测试情况: {project_key}")
            
            test_analysis = await self.analyze_project_testing(repo_path)
            results[project_key] = test_analysis
        
        return results
    
    async def analyze_project_testing(self, repo_path: Path) -> Dict:
        """分析单个项目的测试情况"""
        analysis = {
            'project_path': str(repo_path),
            'has_unit_tests': False,
            'has_test_plan': False,
            'has_test_documentation': False,
            'uses_tdd': False,
            'test_files': [],
            'test_directories': [],
            'test_frameworks': [],
            'test_coverage': 0.0,
            'test_metrics': {
                'total_test_files': 0,
                'total_test_functions': 0,
                'test_file_types': {},
                'test_documentation_files': []
            },
            'analysis_time': datetime.now().isoformat()
        }
        
        try:
            # 1. 检查是否有单元测试
            analysis.update(await self.check_unit_tests(repo_path))
            
            # 2. 检查是否有测试方案
            analysis.update(await self.check_test_plan(repo_path))
            
            # 3. 检查是否有测试文档
            analysis.update(await self.check_test_documentation(repo_path))
            
            # 4. 检查是否使用测试驱动开发
            analysis.update(await self.check_tdd_practices(repo_path))
            
            # 5. 计算测试覆盖率
            analysis['test_coverage'] = await self.calculate_test_coverage(repo_path)
            
        except Exception as e:
            self.logger.error(f"分析项目测试情况失败 {repo_path}: {e}")
        
        return analysis
    
    async def check_unit_tests(self, repo_path: Path) -> Dict:
        """检查是否有单元测试"""
        result = {
            'has_unit_tests': False,
            'test_files': [],
            'test_directories': [],
            'test_frameworks': [],
            'test_metrics': {
                'total_test_files': 0,
                'total_test_functions': 0,
                'test_file_types': {}
            }
        }
        
        # 测试文件模式
        test_patterns = [
            # Python测试文件
            'test_*.py', '*_test.py', 'tests.py',
            # JavaScript/TypeScript测试文件
            '*.test.js', '*.test.ts', '*.test.jsx', '*.test.tsx',
            '*.spec.js', '*.spec.ts', '*.spec.jsx', '*.spec.tsx',
            # Java测试文件
            '*Test.java', '*Tests.java',
            # C#测试文件
            '*Tests.cs', '*Test.cs',
            # 其他测试文件
            '*.test', '*.spec'
        ]
        
        # 测试目录
        test_dirs = ['tests', 'test', '__tests__', 'spec', 'specs', 'testing']
        
        # 测试框架标识
        test_frameworks = {
            'pytest': ['pytest', 'py.test'],
            'unittest': ['unittest', 'unittest2'],
            'jest': ['jest', 'Jest'],
            'mocha': ['mocha', 'Mocha'],
            'jasmine': ['jasmine', 'Jasmine'],
            'junit': ['junit', 'JUnit'],
            'nunit': ['nunit', 'NUnit'],
            'xunit': ['xunit', 'XUnit']
        }
        
        test_files = []
        test_dirs_found = []
        frameworks_found = []
        
        # 查找测试文件
        for pattern in test_patterns:
            for test_file in repo_path.rglob(pattern):
                if test_file.is_file() and '.git' not in str(test_file):
                    test_files.append(str(test_file.relative_to(repo_path)))
                    result['test_metrics']['total_test_files'] += 1
                    
                    # 统计文件类型
                    ext = test_file.suffix.lower()
                    result['test_metrics']['test_file_types'][ext] = \
                        result['test_metrics']['test_file_types'].get(ext, 0) + 1
                    
                    # 检查测试函数数量
                    test_functions = await self.count_test_functions(test_file)
                    result['test_metrics']['total_test_functions'] += test_functions
        
        # 查找测试目录
        for test_dir in test_dirs:
            test_dir_path = repo_path / test_dir
            if test_dir_path.exists() and test_dir_path.is_dir():
                test_dirs_found.append(test_dir)
        
        # 检查测试框架
        for framework, keywords in test_frameworks.items():
            for keyword in keywords:
                # 检查package.json, requirements.txt, pom.xml等配置文件
                config_files = ['package.json', 'requirements.txt', 'pom.xml', 
                               'build.gradle', '*.csproj', '*.sln']
                for config_pattern in config_files:
                    for config_file in repo_path.rglob(config_pattern):
                        if config_file.is_file():
                            try:
                                content = config_file.read_text(encoding='utf-8', errors='ignore')
                                if keyword.lower() in content.lower():
                                    frameworks_found.append(framework)
                                    break
                            except Exception:
                                continue
        
        # 检查测试文件内容中的框架标识
        for test_file in test_files:
            test_file_path = repo_path / test_file
            try:
                content = test_file_path.read_text(encoding='utf-8', errors='ignore')
                for framework, keywords in test_frameworks.items():
                    for keyword in keywords:
                        if keyword.lower() in content.lower():
                            frameworks_found.append(framework)
            except Exception:
                continue
        
        result['test_files'] = test_files
        result['test_directories'] = test_dirs_found
        result['test_frameworks'] = list(set(frameworks_found))
        result['has_unit_tests'] = len(test_files) > 0 or len(test_dirs_found) > 0
        
        return result
    
    async def check_test_plan(self, repo_path: Path) -> Dict:
        """检查是否有测试方案"""
        result = {'has_test_plan': False}
        
        # 测试方案文件模式
        test_plan_patterns = [
            'test_plan*.md', 'test-plan*.md', 'testing_plan*.md', 'testing-plan*.md',
            'test_strategy*.md', 'test-strategy*.md', 'testing_strategy*.md', 'testing-strategy*.md',
            'test_plan*.txt', 'test-plan*.txt', 'testing_plan*.txt', 'testing-plan*.txt',
            'test_strategy*.txt', 'test-strategy*.txt', 'testing_strategy*.txt', 'testing-strategy*.txt',
            'test_plan*.doc', 'test-plan*.doc', 'testing_plan*.doc', 'testing-plan*.doc',
            'test_strategy*.doc', 'test-strategy*.doc', 'testing_strategy*.doc', 'testing-strategy*.doc'
        ]
        
        # 查找测试方案文件
        for pattern in test_plan_patterns:
            for plan_file in repo_path.rglob(pattern):
                if plan_file.is_file() and '.git' not in str(plan_file):
                    result['has_test_plan'] = True
                    break
        
        # 检查README文件中的测试相关内容
        readme_files = ['README.md', 'README.txt', 'readme.md', 'readme.txt']
        for readme_file in readme_files:
            readme_path = repo_path / readme_file
            if readme_path.exists():
                try:
                    content = readme_path.read_text(encoding='utf-8', errors='ignore').lower()
                    test_keywords = ['test plan', 'testing plan', 'test strategy', 'testing strategy',
                                   '测试计划', '测试策略', '测试方案']
                    if any(keyword in content for keyword in test_keywords):
                        result['has_test_plan'] = True
                        break
                except Exception:
                    continue
        
        return result
    
    async def check_test_documentation(self, repo_path: Path) -> Dict:
        """检查是否有测试文档"""
        result = {
            'has_test_documentation': False,
            'test_metrics': {
                'test_documentation_files': []
            }
        }
        
        # 测试文档文件模式
        test_doc_patterns = [
            'test*.md', 'testing*.md', 'test*.txt', 'testing*.txt',
            'test*.doc', 'testing*.doc', 'test*.docx', 'testing*.docx',
            'test*.rst', 'testing*.rst', 'test*.adoc', 'testing*.adoc'
        ]
        
        # 测试文档目录
        test_doc_dirs = ['docs/test', 'docs/testing', 'test/docs', 'testing/docs', 
                        'documentation/test', 'documentation/testing']
        
        test_doc_files = []
        
        # 查找测试文档文件
        for pattern in test_doc_patterns:
            for doc_file in repo_path.rglob(pattern):
                if doc_file.is_file() and '.git' not in str(doc_file):
                    # 排除测试代码文件
                    if not any(doc_file.name.endswith(ext) for ext in ['.py', '.js', '.ts', '.java', '.cs']):
                        test_doc_files.append(str(doc_file.relative_to(repo_path)))
        
        # 查找测试文档目录
        for doc_dir in test_doc_dirs:
            doc_dir_path = repo_path / doc_dir
            if doc_dir_path.exists() and doc_dir_path.is_dir():
                for doc_file in doc_dir_path.rglob('*'):
                    if doc_file.is_file() and doc_file.suffix.lower() in ['.md', '.txt', '.doc', '.docx', '.rst', '.adoc']:
                        test_doc_files.append(str(doc_file.relative_to(repo_path)))
        
        result['test_metrics']['test_documentation_files'] = test_doc_files
        result['has_test_documentation'] = len(test_doc_files) > 0
        
        return result
    
    async def check_tdd_practices(self, repo_path: Path) -> Dict:
        """检查是否使用测试驱动开发"""
        result = {'uses_tdd': False}
        
        # 检查提交历史中的TDD模式
        try:
            # 获取最近的提交历史
            process = await asyncio.create_subprocess_exec(
                'git', 'log', '--oneline', '-20',
                cwd=repo_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                commits = stdout.decode('utf-8').strip().split('\n')
                
                # 检查提交消息中的TDD相关关键词
                tdd_keywords = ['test first', 'test-first', 'tdd', 'test driven', 'test-driven',
                               'red green refactor', 'red-green-refactor', 'fail first', 'fail-first']
                
                tdd_commits = 0
                for commit in commits:
                    commit_lower = commit.lower()
                    if any(keyword in commit_lower for keyword in tdd_keywords):
                        tdd_commits += 1
                
                # 如果超过20%的提交包含TDD关键词，认为使用了TDD
                if len(commits) > 0 and tdd_commits / len(commits) > 0.2:
                    result['uses_tdd'] = True
                    
        except Exception as e:
            self.logger.warning(f"检查TDD实践失败 {repo_path}: {e}")
        
        # 检查测试文件是否在实现文件之前创建
        try:
            # 获取测试文件和实现文件的创建时间
            test_files = []
            impl_files = []
            
            for test_file in repo_path.rglob('test_*.py'):
                if test_file.is_file():
                    test_files.append(test_file)
            
            for impl_file in repo_path.rglob('*.py'):
                if impl_file.is_file() and not impl_file.name.startswith('test_'):
                    impl_files.append(impl_file)
            
            # 检查测试文件是否在实现文件之前创建
            if test_files and impl_files:
                # 这里可以进一步分析文件创建时间，但简化处理
                # 如果测试文件数量与实现文件数量比例合理，可能使用了TDD
                test_impl_ratio = len(test_files) / len(impl_files)
                if 0.1 <= test_impl_ratio <= 1.0:  # 合理的测试覆盖率
                    result['uses_tdd'] = True
                    
        except Exception as e:
            self.logger.warning(f"分析文件创建时间失败 {repo_path}: {e}")
        
        return result
    
    async def count_test_functions(self, test_file: Path) -> int:
        """统计测试文件中的测试函数数量"""
        try:
            content = test_file.read_text(encoding='utf-8', errors='ignore')
            
            # 不同语言的测试函数模式
            test_patterns = [
                # Python
                r'def\s+test_\w+',
                r'class\s+\w*Test\w*',
                # JavaScript/TypeScript
                r'function\s+test\w*',
                r'const\s+test\w*\s*=',
                r'it\s*\(',
                r'describe\s*\(',
                # Java
                r'public\s+void\s+test\w*',
                r'@Test',
                # C#
                r'public\s+void\s+Test\w*',
                r'\[Test\]'
            ]
            
            total_functions = 0
            for pattern in test_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                total_functions += len(matches)
            
            return total_functions
            
        except Exception:
            return 0
    
    async def calculate_test_coverage(self, repo_path: Path) -> float:
        """计算测试覆盖率（简化版本）"""
        try:
            # 统计代码文件和测试文件
            code_files = []
            test_files = []
            
            # 查找代码文件
            code_extensions = ['.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cs', '.cpp', '.c']
            for ext in code_extensions:
                for code_file in repo_path.rglob(f'*{ext}'):
                    if code_file.is_file() and '.git' not in str(code_file):
                        if code_file.name.startswith('test_') or 'test' in code_file.name.lower():
                            test_files.append(code_file)
                        else:
                            code_files.append(code_file)
            
            if len(code_files) == 0:
                return 0.0
            
            # 简化的覆盖率计算：测试文件数量 / 代码文件数量
            coverage = min(len(test_files) / len(code_files), 1.0)
            return round(coverage * 100, 2)
            
        except Exception as e:
            self.logger.warning(f"计算测试覆盖率失败 {repo_path}: {e}")
            return 0.0
    
    async def save_test_analysis_to_db(self, analysis_results: Dict[str, Dict]):
        """将测试分析结果保存到数据库"""
        try:
            async with db.get_db() as conn:
                # 创建测试分析表（如果不存在）
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS project_test_analysis (
                        id SERIAL PRIMARY KEY,
                        project_name VARCHAR(255) NOT NULL UNIQUE,
                        has_unit_tests BOOLEAN DEFAULT FALSE,
                        has_test_plan BOOLEAN DEFAULT FALSE,
                        has_test_documentation BOOLEAN DEFAULT FALSE,
                        uses_tdd BOOLEAN DEFAULT FALSE,
                        test_coverage DECIMAL(5,2) DEFAULT 0.0,
                        test_files TEXT[],
                        test_directories TEXT[],
                        test_frameworks TEXT[],
                        test_metrics JSONB,
                        analysis_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # 插入或更新分析结果
                for project_name, analysis in analysis_results.items():
                    # 将test_metrics转换为JSON字符串
                    import json
                    test_metrics_json = json.dumps(analysis['test_metrics'], ensure_ascii=False)
                    
                    await conn.execute("""
                        INSERT INTO project_test_analysis (
                            project_name, has_unit_tests, has_test_plan, 
                            has_test_documentation, uses_tdd, test_coverage,
                            test_files, test_directories, test_frameworks, test_metrics
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (project_name) 
                        DO UPDATE SET
                            has_unit_tests = EXCLUDED.has_unit_tests,
                            has_test_plan = EXCLUDED.has_test_plan,
                            has_test_documentation = EXCLUDED.has_test_documentation,
                            uses_tdd = EXCLUDED.uses_tdd,
                            test_coverage = EXCLUDED.test_coverage,
                            test_files = EXCLUDED.test_files,
                            test_directories = EXCLUDED.test_directories,
                            test_frameworks = EXCLUDED.test_frameworks,
                            test_metrics = EXCLUDED.test_metrics,
                            updated_at = CURRENT_TIMESTAMP
                    """, (
                        project_name,
                        analysis['has_unit_tests'],
                        analysis['has_test_plan'],
                        analysis['has_test_documentation'],
                        analysis['uses_tdd'],
                        analysis['test_coverage'],
                        analysis['test_files'],
                        analysis['test_directories'],
                        analysis['test_frameworks'],
                        test_metrics_json
                    ))
                
                await conn.commit()
                self.logger.info(f"成功保存 {len(analysis_results)} 个项目的测试分析结果")
                
        except Exception as e:
            self.logger.error(f"保存测试分析结果失败: {e}")
    
    async def get_test_analysis_summary(self) -> Dict:
        """获取测试分析摘要"""
        try:
            async with db.get_db() as conn:
                # 获取总体统计
                result = await conn.execute("""
                    SELECT 
                        COUNT(*) as total_projects,
                        SUM(CASE WHEN has_unit_tests THEN 1 ELSE 0 END) as projects_with_unit_tests,
                        SUM(CASE WHEN has_test_plan THEN 1 ELSE 0 END) as projects_with_test_plan,
                        SUM(CASE WHEN has_test_documentation THEN 1 ELSE 0 END) as projects_with_test_docs,
                        SUM(CASE WHEN uses_tdd THEN 1 ELSE 0 END) as projects_using_tdd,
                        AVG(test_coverage) as avg_test_coverage
                    FROM project_test_analysis
                """)
                result = await result.fetchone()
                
                # 获取测试框架分布
                framework_result = await conn.execute("""
                    SELECT 
                        framework,
                        COUNT(*) as project_count
                    FROM (
                        SELECT unnest(test_frameworks) as framework
                        FROM project_test_analysis
                        WHERE test_frameworks IS NOT NULL AND array_length(test_frameworks, 1) > 0
                    ) frameworks
                    GROUP BY framework
                    ORDER BY project_count DESC
                """)
                framework_stats = await framework_result.fetchall()
                
                # 获取测试覆盖率分布
                coverage_result = await conn.execute("""
                    SELECT 
                        CASE 
                            WHEN test_coverage = 0 THEN '无测试'
                            WHEN test_coverage < 25 THEN '低覆盖率 (0-25%)'
                            WHEN test_coverage < 50 THEN '中等覆盖率 (25-50%)'
                            WHEN test_coverage < 75 THEN '高覆盖率 (50-75%)'
                            ELSE '很高覆盖率 (75%+)'
                        END as coverage_level,
                        COUNT(*) as project_count
                    FROM project_test_analysis
                    GROUP BY coverage_level
                    ORDER BY project_count DESC
                """)
                coverage_stats = await coverage_result.fetchall()
                
                return {
                    'summary': dict(result) if result else {},
                    'framework_distribution': [dict(row) for row in framework_stats],
                    'coverage_distribution': [dict(row) for row in coverage_stats]
                }
                
        except Exception as e:
            self.logger.error(f"获取测试分析摘要失败: {e}")
            return {} 