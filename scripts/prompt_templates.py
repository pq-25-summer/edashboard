#!/usr/bin/env python3
"""
提示词模板工具
用于生成各种分析任务的AI提示词
"""

import json
from typing import Dict, Any, List
from pathlib import Path


class PromptTemplates:
    """提示词模板管理器"""
    
    def __init__(self):
        self.templates = self._load_templates()
    
    def _load_templates(self) -> Dict[str, str]:
        """加载提示词模板"""
        return {
            "project_analysis": self._get_project_analysis_template(),
            "code_review": self._get_code_review_template(),
            "tech_stack_analysis": self._get_tech_stack_template(),
            "readme_analysis": self._get_readme_analysis_template(),
            "git_analysis": self._get_git_analysis_template(),
            "quality_assessment": self._get_quality_assessment_template(),
            "improvement_suggestions": self._get_improvement_suggestions_template(),
            "report_generation": self._get_report_generation_template(),
            "error_diagnosis": self._get_error_diagnosis_template(),
            "feature_planning": self._get_feature_planning_template()
        }
    
    def get_template(self, template_name: str) -> str:
        """获取指定模板"""
        return self.templates.get(template_name, "")
    
    def format_template(self, template_name: str, **kwargs) -> str:
        """格式化模板"""
        template = self.get_template(template_name)
        try:
            return template.format(**kwargs)
        except KeyError as e:
            print(f"警告: 模板格式化失败，缺少参数: {e}")
            return template
    
    def _get_project_analysis_template(self) -> str:
        """项目分析模板"""
        return """
请对以下GitHub项目进行全面的代码质量分析：

## 项目基本信息
- 项目名称: {project_name}
- GitHub仓库: {github_url}
- 主要编程语言: {main_language}
- 项目大小: {project_size} KB
- 文件总数: {total_files}

## 项目结构分析
{file_structure_summary}

## Git活动分析
- 提交次数: {commit_count}
- 贡献者数量: {contributors}
- 最后提交时间: {last_commit}
- 当前分支: {current_branch}

## 技术栈信息
{tech_stack_info}

## 分析要求
请从以下维度进行评估：

### 1. 代码质量评分 (0-100分)
- 代码规范性
- 项目结构合理性
- 文档完整性
- 配置规范性

### 2. 开发活跃度评估
- 提交频率分析
- 团队协作情况
- 项目维护状态

### 3. 技术栈评估
- 技术选型合理性
- 框架使用情况
- 依赖管理

### 4. 项目完整性
- 必要文件检查
- 配置文件完整性
- 部署配置

### 5. 改进建议
- 代码质量提升
- 项目结构优化
- 技术栈改进
- 文档完善

请用中文回答，格式要清晰，包含具体的评分和建议。
"""
    
    def _get_code_review_template(self) -> str:
        """代码审查模板"""
        return """
请对以下代码文件进行详细的代码审查：

## 文件信息
- 文件路径: {file_path}
- 文件类型: {file_type}
- 文件大小: {file_size} bytes
- 代码行数: {line_count}

## 代码内容
```{language}
{code_content}
```

## 审查要求
请从以下方面进行详细分析：

### 1. 代码规范性 (1-10分)
- 命名规范
- 代码格式
- 注释质量
- 代码风格

### 2. 代码质量 (1-10分)
- 逻辑清晰度
- 代码复杂度
- 可读性
- 可维护性

### 3. 错误处理 (1-10分)
- 异常处理
- 边界条件
- 输入验证
- 错误信息

### 4. 性能考虑 (1-10分)
- 算法效率
- 内存使用
- 资源管理
- 优化空间

### 5. 安全性 (1-10分)
- 输入验证
- 数据保护
- 权限控制
- 安全漏洞

### 6. 具体问题
列出发现的具体问题，包括：
- 问题描述
- 严重程度
- 修复建议
- 最佳实践

### 7. 改进建议
提供具体的改进建议和代码示例。

请给出详细的评分和具体的改进建议。
"""
    
    def _get_tech_stack_template(self) -> str:
        """技术栈分析模板"""
        return """
请分析以下项目的技术栈使用情况：

## 项目信息
- 项目名称: {project_name}
- 项目类型: {project_type}

## 文件列表
{file_list}

## 配置文件内容
{config_files}

## 分析要求
请详细分析以下技术栈：

### 1. 编程语言
- 主要语言: {main_languages}
- 语言分布: {language_distribution}
- 语言选择合理性

### 2. 前端技术栈
- 框架: {frontend_frameworks}
- UI库: {ui_libraries}
- 构建工具: {build_tools}
- 包管理器: {package_managers}

### 3. 后端技术栈
- 框架: {backend_frameworks}
- 数据库: {databases}
- 缓存: {caching}
- 消息队列: {message_queues}

### 4. 部署和运维
- 容器化: {containerization}
- 编排工具: {orchestration}
- 监控: {monitoring}
- CI/CD: {cicd}

### 5. AI/ML技术 (如果有)
- 模型: {ai_models}
- 框架: {ai_frameworks}
- 库: {ai_libraries}
- 运行时: {ai_runtimes}

### 6. 技术栈评估
- 技术选型合理性
- 版本兼容性
- 社区活跃度
- 学习曲线

### 7. 改进建议
- 技术栈优化
- 版本升级建议
- 替代方案
- 最佳实践

请按类别整理，标注使用频率和重要性。
"""
    
    def _get_readme_analysis_template(self) -> str:
        """README分析模板"""
        return """
请分析以下项目的README文档质量：

## 项目信息
- 项目名称: {project_name}
- README文件: {readme_files}

## README内容
{readme_content}

## 分析要求
请从以下维度评估README质量：

### 1. 内容完整性 (1-10分)
- 项目描述
- 功能特性
- 安装说明
- 使用示例
- API文档
- 贡献指南

### 2. 文档结构 (1-10分)
- 标题层次
- 内容组织
- 导航便利性
- 格式规范

### 3. 可读性 (1-10分)
- 语言表达
- 技术术语
- 示例质量
- 图表使用

### 4. 实用性 (1-10分)
- 快速上手
- 问题解决
- 常见问题
- 联系方式

### 5. 维护性 (1-10分)
- 更新频率
- 版本同步
- 链接有效性
- 内容准确性

### 6. 具体问题
列出发现的问题：
- 缺失内容
- 错误信息
- 过时内容
- 格式问题

### 7. 改进建议
提供具体的改进建议和示例。

请给出详细的评分和具体的改进建议。
"""
    
    def _get_git_analysis_template(self) -> str:
        """Git活动分析模板"""
        return """
请分析以下项目的Git活动情况：

## 项目信息
- 项目名称: {project_name}
- 分析时间范围: {time_range}

## Git统计信息
- 总提交数: {total_commits}
- 贡献者数: {contributors}
- 分支数: {branches}
- 标签数: {tags}
- 最后提交: {last_commit}

## 提交详情
{commit_details}

## 分支信息
{branch_info}

## 分析要求
请从以下维度分析Git活动：

### 1. 开发活跃度 (1-10分)
- 提交频率
- 提交规律
- 开发持续性
- 项目活跃度

### 2. 团队协作 (1-10分)
- 贡献者分布
- 协作模式
- 代码审查
- 冲突解决

### 3. 代码管理 (1-10分)
- 分支策略
- 提交规范
- 版本管理
- 发布流程

### 4. 提交质量 (1-10分)
- 提交信息质量
- 代码变更合理性
- 功能完整性
- 测试覆盖

### 5. 项目健康度
- 维护状态
- 更新频率
- 问题响应
- 社区活跃度

### 6. 改进建议
- 工作流程优化
- 协作模式改进
- 代码管理提升
- 自动化建议

请给出详细的分析和建议。
"""
    
    def _get_quality_assessment_template(self) -> str:
        """质量评估模板"""
        return """
请对以下项目进行全面的质量评估：

## 项目概况
- 项目名称: {project_name}
- 项目类型: {project_type}
- 开发阶段: {development_stage}

## 评估数据
{assessment_data}

## 评估维度

### 1. 代码质量 (权重: 30%)
- 代码规范性
- 复杂度控制
- 可读性
- 可维护性

### 2. 项目结构 (权重: 20%)
- 目录组织
- 模块划分
- 依赖管理
- 配置管理

### 3. 文档质量 (权重: 15%)
- README完整性
- API文档
- 代码注释
- 使用说明

### 4. 开发活跃度 (权重: 15%)
- 提交频率
- 更新及时性
- 问题响应
- 功能完善度

### 5. 技术选型 (权重: 10%)
- 技术栈合理性
- 版本选择
- 性能考虑
- 扩展性

### 6. 测试覆盖 (权重: 10%)
- 单元测试
- 集成测试
- 测试覆盖率
- 测试质量

## 评分标准
- 优秀 (90-100分): 项目质量很高，可以作为标杆
- 良好 (80-89分): 项目质量良好，有少量改进空间
- 一般 (70-79分): 项目质量一般，需要改进
- 较差 (60-69分): 项目质量较差，需要大幅改进
- 很差 (0-59分): 项目质量很差，需要重构

请给出：
1. 各维度详细评分
2. 总体评分和等级
3. 主要问题分析
4. 改进优先级建议
5. 具体改进措施
"""
    
    def _get_improvement_suggestions_template(self) -> str:
        """改进建议模板"""
        return """
请为以下项目提供详细的改进建议：

## 项目现状
- 项目名称: {project_name}
- 当前评分: {current_score}
- 主要问题: {main_issues}

## 项目详情
{project_details}

## 改进建议要求

### 1. 优先级分类
请将建议按以下优先级分类：
- **高优先级**: 严重影响项目质量，需要立即解决
- **中优先级**: 影响项目质量，建议近期解决
- **低优先级**: 可以优化，但不紧急

### 2. 改进领域
请从以下领域提供建议：
- 代码质量改进
- 项目结构优化
- 文档完善
- 测试加强
- 性能优化
- 安全加固
- 部署优化
- 监控完善

### 3. 建议格式
每个建议应包含：
- 问题描述
- 影响分析
- 解决方案
- 实施步骤
- 预期效果
- 所需资源

### 4. 实施计划
请提供：
- 短期计划 (1-2周)
- 中期计划 (1-2月)
- 长期计划 (3-6月)

### 5. 成功指标
为每个建议提供可衡量的成功指标。

请提供具体、可操作的改进建议。
"""
    
    def _get_report_generation_template(self) -> str:
        """报告生成模板"""
        return """
请为以下项目生成详细的分析报告：

## 项目信息
{project_info}

## 分析数据
{analysis_data}

## 报告要求

### 1. 报告结构
请按以下结构组织报告：
- 执行摘要
- 项目概述
- 技术分析
- 质量评估
- 风险评估
- 改进建议
- 结论

### 2. 内容要求
- 使用Markdown格式
- 包含适当的图表建议
- 使用emoji图标增强可读性
- 提供数据支撑
- 包含具体示例

### 3. 分析深度
- 技术栈详细分析
- 代码质量量化评估
- 开发活跃度趋势分析
- 项目健康度评估
- 竞争力分析

### 4. 建议质量
- 具体可操作
- 优先级明确
- 资源需求评估
- 时间规划
- 成功指标

### 5. 报告风格
- 专业客观
- 数据驱动
- 逻辑清晰
- 易于理解
- 行动导向

请生成一份专业、全面的项目分析报告。
"""
    
    def _get_error_diagnosis_template(self) -> str:
        """错误诊断模板"""
        return """
请帮助诊断以下错误：

## 错误信息
{error_message}

## 错误上下文
- 发生时间: {error_time}
- 操作环境: {environment}
- 相关代码: {related_code}
- 错误堆栈: {error_stack}

## 诊断要求

### 1. 错误分析
- 错误类型识别
- 根本原因分析
- 触发条件分析
- 影响范围评估

### 2. 解决方案
- 立即修复方案
- 根本解决措施
- 预防措施
- 验证方法

### 3. 相关知识
- 相关技术文档
- 最佳实践
- 常见陷阱
- 学习资源

### 4. 调试建议
- 调试工具推荐
- 调试步骤
- 日志分析
- 测试方法

请提供详细的诊断和解决方案。
"""
    
    def _get_feature_planning_template(self) -> str:
        """功能规划模板"""
        return """
请为以下功能需求制定详细的实现计划：

## 功能需求
{feature_requirements}

## 项目现状
- 技术栈: {current_tech_stack}
- 项目结构: {project_structure}
- 现有功能: {existing_features}

## 规划要求

### 1. 技术方案
- 技术选型
- 架构设计
- 数据模型
- 接口设计

### 2. 实现计划
- 开发阶段划分
- 时间估算
- 资源需求
- 里程碑设定

### 3. 风险评估
- 技术风险
- 时间风险
- 资源风险
- 质量风险

### 4. 测试策略
- 测试计划
- 测试用例
- 测试环境
- 验收标准

### 5. 部署方案
- 部署策略
- 环境配置
- 监控方案
- 回滚计划

### 6. 文档要求
- 技术文档
- 用户文档
- API文档
- 运维文档

请提供详细的功能实现规划。
"""


def main():
    """主函数 - 用于测试模板"""
    templates = PromptTemplates()
    
    # 测试模板格式化
    test_data = {
        "project_name": "测试项目",
        "github_url": "https://github.com/test/project",
        "main_language": "Python",
        "total_files": 50,
        "code_files": 30,
        "doc_files": 5,
        "file_structure": "项目结构示例",
        "commit_count": 100,
        "contributors": 5,
        "last_commit": "2024-01-01",
        "current_branch": "main"
    }
    
    # 生成项目分析提示词
    prompt = templates.format_template("project_analysis", **test_data)
    print("=== 项目分析提示词 ===")
    print(prompt)
    print("\n" + "="*50 + "\n")
    
    # 保存模板到文件
    output_file = Path("prompt_templates_output.md")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("# 提示词模板示例\n\n")
        for name, template in templates.templates.items():
            f.write(f"## {name}\n\n")
            f.write("```\n")
            f.write(template)
            f.write("\n```\n\n")
    
    print(f"✅ 模板已保存到: {output_file}")


if __name__ == "__main__":
    main() 