# 测试分析功能使用说明

## 概述

本功能实现了Issue #4的需求：**统计各项目的测试情况**。通过分析本地Git仓库，自动检测和统计各项目的测试实践情况。

## 功能特性

### 分析内容
- ✅ **是否有单元测试** - 检测项目中的测试文件和测试目录
- ✅ **是否有测试方案** - 查找测试计划、测试策略等相关文档
- ✅ **是否有对应的文档** - 识别测试相关的文档文件
- ✅ **是否使用测试驱动开发** - 通过提交历史和文件结构分析TDD实践

### 支持的测试框架
- **Python**: pytest, unittest, unittest2
- **JavaScript/TypeScript**: Jest, Mocha, Jasmine
- **Java**: JUnit
- **C#**: NUnit, XUnit
- **其他**: 通用测试文件模式识别

### 检测的文件类型
- 测试文件: `test_*.py`, `*.test.js`, `*Test.java`, `*Tests.cs` 等
- 测试目录: `tests/`, `test/`, `__tests__/`, `spec/` 等
- 测试文档: `test_plan*.md`, `testing*.md`, `test*.txt` 等
- 配置文件: `package.json`, `requirements.txt`, `pom.xml` 等

## 使用方法

### 1. 命令行脚本

运行独立的测试分析脚本：

```bash
cd scripts
python analyze_testing.py
```

脚本会：
- 分析所有本地Git仓库的测试情况
- 将结果保存到数据库
- 生成JSON和Markdown格式的报告
- 在控制台显示分析摘要

### 2. API接口

#### 分析所有项目
```bash
curl -X POST http://localhost:8000/api/test-analysis/analyze-all
```

#### 获取分析摘要
```bash
curl http://localhost:8000/api/test-analysis/summary
```

#### 获取所有项目测试情况
```bash
curl http://localhost:8000/api/test-analysis/projects
```

#### 获取指定项目测试情况
```bash
curl http://localhost:8000/api/test-analysis/projects/{project_name}
```

#### 刷新指定项目分析
```bash
curl -X POST http://localhost:8000/api/test-analysis/refresh/{project_name}
```

#### 获取详细统计信息
```bash
curl http://localhost:8000/api/test-analysis/statistics
```

### 3. Web界面

1. 启动后端服务：
```bash
cd backend
python main.py
```

2. 启动前端服务：
```bash
cd frontend
npm run dev
```

3. 访问测试分析页面：
   - 打开浏览器访问 `http://localhost:5173`
   - 点击导航栏中的"测试分析"
   - 查看各项目的测试情况统计

## 输出结果

### 控制台输出示例
```
============================================================
测试分析结果摘要
============================================================
📊 总项目数: 25
🧪 有单元测试的项目: 18
📋 有测试方案的项目: 12
📚 有测试文档的项目: 15
🔄 使用TDD的项目: 8
📈 平均测试覆盖率: 45.67%

📊 测试框架使用情况:
  - pytest: 12 个项目
  - jest: 8 个项目
  - unittest: 6 个项目
  - junit: 4 个项目

📈 测试覆盖率分布:
  - 无测试: 7 个项目
  - 低覆盖率 (0-25%): 8 个项目
  - 中等覆盖率 (25-50%): 6 个项目
  - 高覆盖率 (50-75%): 3 个项目
  - 很高覆盖率 (75%+): 1 个项目
```

### 数据库表结构

分析结果保存在 `project_test_analysis` 表中：

```sql
CREATE TABLE project_test_analysis (
    id SERIAL PRIMARY KEY,
    project_name VARCHAR(255) NOT NULL,
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
);
```

### 报告文件

脚本会生成以下报告文件：

1. **JSON报告**: `docs/test_analysis_report.json`
   - 包含完整的分析数据
   - 可用于进一步的数据处理

2. **Markdown报告**: `docs/test_analysis_report.md`
   - 格式化的分析报告
   - 包含统计表格和详细结果

## 配置说明

### 环境变量

确保在 `backend/app/config.py` 中正确配置：

```python
class Settings(BaseSettings):
    # 本地仓库目录路径
    local_repos_dir: str = "/path/to/your/repos"
    
    # 数据库连接
    database_url: str = "postgresql://user:password@localhost/dbname"
```

### 目录结构要求

本地仓库目录应该包含多个Git仓库，每个仓库代表一个项目：

```
local_repos_dir/
├── project1/
│   ├── .git/
│   ├── src/
│   ├── tests/
│   └── README.md
├── project2/
│   ├── .git/
│   ├── app/
│   ├── test/
│   └── package.json
└── ...
```

## 注意事项

1. **性能考虑**: 分析大量项目可能需要较长时间，建议在非高峰期运行
2. **文件权限**: 确保脚本有读取本地仓库目录的权限
3. **Git要求**: 需要Git命令行工具可用
4. **数据库**: 确保PostgreSQL数据库正在运行且可连接
5. **编码问题**: 某些文件可能包含特殊字符，脚本会尝试处理编码问题

## 故障排除

### 常见问题

1. **找不到项目**: 检查 `local_repos_dir` 配置是否正确
2. **数据库连接失败**: 检查数据库服务是否运行，连接字符串是否正确
3. **权限错误**: 确保有读取仓库目录的权限
4. **编码错误**: 某些文件可能包含特殊字符，脚本会跳过这些文件

### 调试模式

启用详细日志输出：

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 扩展功能

### 自定义测试模式

可以在 `TestAnalyzer` 类中添加自定义的测试文件模式：

```python
# 在 check_unit_tests 方法中添加
custom_patterns = ['custom_test_*.py', 'my_tests/*.js']
```

### 新的测试框架支持

在 `test_frameworks` 字典中添加新的框架标识：

```python
test_frameworks = {
    'new_framework': ['new_framework', 'NewFramework'],
    # ... 现有框架
}
```

## 更新日志

- **v1.0.0**: 初始版本，实现基本的测试分析功能
- 支持多种编程语言的测试框架检测
- 提供Web界面和API接口
- 生成详细的分析报告 