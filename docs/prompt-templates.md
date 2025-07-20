# 提示词模板使用说明

## 概述

本项目提供了多种提示词模板，用于标准化AI辅助开发和分析任务。这些模板确保了一致性、完整性和高质量的输出。

## 模板位置

### 1. Cursor IDE 配置 (`.cursorrules`)
- **位置**: 项目根目录的 `.cursorrules` 文件
- **用途**: Cursor IDE 自动读取，每次对话都会应用
- **内容**: 项目规范、编码标准、任务模式

### 2. 后端提示词配置 (`backend/app/prompts.py`)
- **位置**: `backend/app/prompts.py`
- **用途**: 后端API中的AI功能提示词
- **内容**: 项目分析、技术栈分析、代码质量评估等

### 3. 脚本工具提示词 (`scripts/prompt_templates.py`)
- **位置**: `scripts/prompt_templates.py`
- **用途**: 脚本工具中的分析任务提示词
- **内容**: 项目分析、报告生成、错误诊断等

## 模板类型

### 1. 项目分析模板

#### 使用场景
- GitHub项目代码质量分析
- 项目结构评估
- 开发活跃度分析

#### 模板参数
```python
{
    "project_name": "项目名称",
    "github_url": "GitHub仓库URL",
    "main_language": "主要编程语言",
    "project_size": "项目大小(KB)",
    "total_files": "文件总数",
    "file_structure_summary": "项目结构摘要",
    "commit_count": "提交次数",
    "contributors": "贡献者数量",
    "last_commit": "最后提交时间",
    "current_branch": "当前分支",
    "tech_stack_info": "技术栈信息"
}
```

#### 使用示例
```python
from scripts.prompt_templates import PromptTemplates

templates = PromptTemplates()
prompt = templates.format_template("project_analysis", **project_data)
```

### 2. 代码审查模板

#### 使用场景
- 代码质量评估
- 代码规范性检查
- 安全性分析

#### 模板参数
```python
{
    "file_path": "文件路径",
    "file_type": "文件类型",
    "file_size": "文件大小",
    "line_count": "代码行数",
    "language": "编程语言",
    "code_content": "代码内容"
}
```

### 3. 技术栈分析模板

#### 使用场景
- 项目技术栈识别
- 框架和库分析
- AI技术检测

#### 模板参数
```python
{
    "project_name": "项目名称",
    "project_type": "项目类型",
    "file_list": "文件列表",
    "config_files": "配置文件内容",
    "main_languages": "主要语言",
    "language_distribution": "语言分布",
    "frontend_frameworks": "前端框架",
    "backend_frameworks": "后端框架",
    "databases": "数据库",
    "ai_models": "AI模型",
    "ai_frameworks": "AI框架"
}
```

### 4. README分析模板

#### 使用场景
- README文档质量评估
- 文档完整性检查
- 改进建议生成

#### 模板参数
```python
{
    "project_name": "项目名称",
    "readme_files": "README文件列表",
    "readme_content": "README内容"
}
```

### 5. Git活动分析模板

#### 使用场景
- Git提交活动分析
- 团队协作评估
- 开发活跃度分析

#### 模板参数
```python
{
    "project_name": "项目名称",
    "time_range": "分析时间范围",
    "total_commits": "总提交数",
    "contributors": "贡献者数",
    "branches": "分支数",
    "tags": "标签数",
    "last_commit": "最后提交",
    "commit_details": "提交详情",
    "branch_info": "分支信息"
}
```

### 6. 质量评估模板

#### 使用场景
- 项目整体质量评估
- 多维度评分
- 改进优先级排序

#### 模板参数
```python
{
    "project_name": "项目名称",
    "project_type": "项目类型",
    "development_stage": "开发阶段",
    "assessment_data": "评估数据"
}
```

### 7. 改进建议模板

#### 使用场景
- 项目改进建议生成
- 优先级排序
- 实施计划制定

#### 模板参数
```python
{
    "project_name": "项目名称",
    "current_score": "当前评分",
    "main_issues": "主要问题",
    "project_details": "项目详情"
}
```

### 8. 报告生成模板

#### 使用场景
- 项目分析报告生成
- 技术文档编写
- 评估报告制作

#### 模板参数
```python
{
    "project_info": "项目信息",
    "analysis_data": "分析数据"
}
```

### 9. 错误诊断模板

#### 使用场景
- 错误原因分析
- 解决方案提供
- 调试建议

#### 模板参数
```python
{
    "error_message": "错误信息",
    "error_time": "发生时间",
    "environment": "操作环境",
    "related_code": "相关代码",
    "error_stack": "错误堆栈"
}
```

### 10. 功能规划模板

#### 使用场景
- 新功能实现规划
- 技术方案设计
- 开发计划制定

#### 模板参数
```python
{
    "feature_requirements": "功能需求",
    "current_tech_stack": "当前技术栈",
    "project_structure": "项目结构",
    "existing_features": "现有功能"
}
```

## 使用方法

### 1. 在脚本中使用

```python
#!/usr/bin/env python3
from scripts.prompt_templates import PromptTemplates

def analyze_project(project_data):
    templates = PromptTemplates()
    
    # 生成项目分析提示词
    analysis_prompt = templates.format_template(
        "project_analysis", 
        **project_data
    )
    
    # 发送给AI进行分析
    # result = send_to_ai(analysis_prompt)
    
    return analysis_prompt
```

### 2. 在后端API中使用

```python
from backend.app.prompts import PROJECT_ANALYSIS_PROMPT

def analyze_project_api(project_info):
    # 格式化提示词
    prompt = PROJECT_ANALYSIS_PROMPT.format(
        project_name=project_info.name,
        github_url=project_info.url,
        # ... 其他参数
    )
    
    # 调用AI服务
    # result = call_ai_service(prompt)
    
    return prompt
```

### 3. 在Cursor IDE中使用

`.cursorrules` 文件会自动被Cursor IDE读取，每次对话都会应用其中的规则和模式。

## 自定义模板

### 1. 添加新模板

在 `scripts/prompt_templates.py` 中添加新模板：

```python
def _get_custom_template(self) -> str:
    """自定义模板"""
    return """
请对以下内容进行分析：

## 分析内容
{content}

## 分析要求
{requirements}

请提供详细的分析结果。
"""
```

### 2. 注册新模板

在 `_load_templates` 方法中注册：

```python
def _load_templates(self) -> Dict[str, str]:
    return {
        # ... 现有模板
        "custom_analysis": self._get_custom_template(),
    }
```

### 3. 使用新模板

```python
prompt = templates.format_template("custom_analysis", 
    content="分析内容",
    requirements="分析要求"
)
```

## 最佳实践

### 1. 模板设计原则
- **明确性**: 模板要求要明确具体
- **结构化**: 使用清晰的层次结构
- **可扩展**: 支持参数化配置
- **一致性**: 保持格式和风格一致

### 2. 参数管理
- 使用有意义的参数名
- 提供默认值处理
- 添加参数验证
- 记录参数说明

### 3. 错误处理
- 处理参数缺失情况
- 提供友好的错误信息
- 支持模板回退机制

### 4. 性能优化
- 避免重复模板加载
- 缓存格式化结果
- 优化大模板处理

## 维护和更新

### 1. 版本控制
- 模板变更需要版本记录
- 保持向后兼容性
- 更新使用文档

### 2. 质量保证
- 定期审查模板质量
- 收集使用反馈
- 持续优化改进

### 3. 测试验证
- 测试模板格式化
- 验证AI输出质量
- 检查参数完整性

## 常见问题

### 1. 模板格式化失败
**问题**: 参数不匹配导致格式化失败
**解决**: 检查参数名和数量，使用try-catch处理

### 2. 输出质量不稳定
**问题**: AI输出质量参差不齐
**解决**: 优化模板结构，增加具体要求和示例

### 3. 模板维护困难
**问题**: 模板数量多，维护复杂
**解决**: 建立模板分类体系，使用自动化工具

## 相关文档

- [项目分析功能说明](project-status-feature.md)
- [技术栈分析说明](ISSUE_5_SOLUTION.md)
- [环境配置说明](environment-setup.md)
- [API文档](../backend/README.md) 