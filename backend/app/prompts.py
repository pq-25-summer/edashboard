"""
提示词模板配置文件
包含项目中常用的AI提示词模板
"""

# 项目分析提示词模板
PROJECT_ANALYSIS_PROMPT = """
请分析以下GitHub项目的代码质量和开发情况：

项目信息：
- 项目名称: {project_name}
- GitHub URL: {github_url}
- 主要语言: {main_language}
- 文件数量: {total_files}
- 代码文件: {code_files}
- 文档文件: {doc_files}

项目结构：
{file_structure}

Git信息：
- 提交次数: {commit_count}
- 贡献者数: {contributors}
- 最后提交: {last_commit}
- 当前分支: {current_branch}

请从以下方面进行评估：
1. 代码质量评分（0-100分）
2. 项目完整性评估
3. 开发活跃度分析
4. 改进建议
5. 技术栈识别

请用中文回答，格式要清晰易读。
"""

# 技术栈分析提示词模板
TECH_STACK_ANALYSIS_PROMPT = """
请分析以下项目的技术栈使用情况：

项目文件列表：
{file_list}

配置文件内容：
{config_files}

请识别并分析：
1. 主要编程语言
2. 使用的框架和库
3. 数据库技术
4. 部署和容器化技术
5. AI/ML相关技术（如果有）
6. 前端技术栈
7. 后端技术栈

请按类别整理，并标注使用频率（主要/次要/少量）。
"""

# 代码质量评估提示词模板
CODE_QUALITY_PROMPT = """
请评估以下代码文件的质量：

文件路径: {file_path}
文件类型: {file_type}
代码内容:
{code_content}

请从以下维度进行评估：
1. 代码规范性（命名、格式、注释）
2. 代码复杂度
3. 错误处理
4. 性能考虑
5. 安全性
6. 可维护性

给出具体的评分（1-10分）和改进建议。
"""

# 项目报告生成提示词模板
PROJECT_REPORT_PROMPT = """
请为以下项目生成详细的分析报告：

项目基本信息：
{project_info}

分析数据：
{analysis_data}

请生成包含以下内容的报告：
1. 项目概述
2. 技术栈分析
3. 代码质量评估
4. 开发活跃度分析
5. 项目优势
6. 改进建议
7. 总体评分

报告格式要求：
- 使用Markdown格式
- 包含适当的emoji图标
- 数据可视化建议
- 清晰的结构层次
"""

# 错误诊断提示词模板
ERROR_DIAGNOSIS_PROMPT = """
请帮助诊断以下错误：

错误信息：
{error_message}

错误上下文：
{error_context}

相关代码：
{related_code}

请提供：
1. 错误原因分析
2. 解决方案建议
3. 预防措施
4. 相关文档链接
"""

# 功能实现建议提示词模板
FEATURE_IMPLEMENTATION_PROMPT = """
请为以下功能需求提供实现建议：

功能描述：
{feature_description}

当前技术栈：
{current_tech_stack}

项目结构：
{project_structure}

请提供：
1. 技术方案建议
2. 实现步骤
3. 代码示例
4. 注意事项
5. 测试建议
"""

# 数据库设计提示词模板
DATABASE_DESIGN_PROMPT = """
请为以下业务需求设计数据库表结构：

业务需求：
{business_requirements}

现有表结构：
{existing_tables}

请设计：
1. 新表结构（字段名、类型、约束）
2. 表关系设计
3. 索引建议
4. 数据迁移方案
5. SQL创建语句
"""

# API设计提示词模板
API_DESIGN_PROMPT = """
请为以下功能设计RESTful API：

功能需求：
{feature_requirements}

现有API结构：
{existing_apis}

请设计：
1. API端点定义
2. 请求/响应模型
3. 状态码设计
4. 错误处理
5. 认证授权
6. 示例代码
"""

# 前端组件设计提示词模板
FRONTEND_COMPONENT_PROMPT = """
请为以下需求设计React组件：

组件需求：
{component_requirements}

技术栈：
- React 18+
- TypeScript
- React Bootstrap
- ECharts (如果需要图表)

请提供：
1. 组件结构设计
2. Props接口定义
3. 状态管理方案
4. 样式建议
5. 完整代码示例
6. 使用示例
"""

# 部署配置提示词模板
DEPLOYMENT_CONFIG_PROMPT = """
请为以下应用提供部署配置建议：

应用信息：
{app_info}

部署环境：
{deployment_environment}

请提供：
1. Docker配置
2. Kubernetes配置
3. 环境变量配置
4. 健康检查配置
5. 资源限制建议
6. 监控配置
"""

# 测试策略提示词模板
TESTING_STRATEGY_PROMPT = """
请为以下功能制定测试策略：

功能描述：
{feature_description}

技术栈：
{tech_stack}

请制定：
1. 单元测试策略
2. 集成测试策略
3. 端到端测试策略
4. 测试用例设计
5. 测试工具建议
6. 测试数据准备
"""

# 性能优化提示词模板
PERFORMANCE_OPTIMIZATION_PROMPT = """
请为以下性能问题提供优化建议：

性能问题：
{performance_issue}

系统架构：
{system_architecture}

当前指标：
{current_metrics}

请提供：
1. 性能瓶颈分析
2. 优化方案
3. 代码优化建议
4. 数据库优化
5. 缓存策略
6. 监控指标
"""

# 安全加固提示词模板
SECURITY_HARDENING_PROMPT = """
请为以下应用提供安全加固建议：

应用类型：
{app_type}

当前安全措施：
{current_security}

请提供：
1. 安全风险评估
2. 认证授权加固
3. 数据保护措施
4. API安全配置
5. 输入验证
6. 日志监控
7. 应急响应
""" 