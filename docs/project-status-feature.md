# 项目状态功能说明

## 概述

项目状态功能是看板系统的新增功能，用于实时监控和分析所有项目的状态信息，包括代码质量、文档完整性、开发活跃度等指标。

## 功能特性

### 🔍 项目分析
- **文件结构分析**: 统计代码文件、文档文件、配置文件数量
- **编程语言识别**: 自动识别项目主要编程语言
- **README检查**: 检测项目是否包含README文档
- **配置检查**: 检查package.json、requirements.txt、Docker配置等
- **项目大小统计**: 计算项目总大小

### 📊 开发活跃度分析
- **提交统计**: 统计Git提交次数
- **贡献者统计**: 统计项目贡献者数量
- **分支信息**: 获取当前分支信息
- **最后提交**: 记录最后提交信息

### 🏆 质量评分系统
- **README文档** (25分): 检查是否包含README文件
- **代码文件** (25分): 检查是否包含代码文件
- **项目配置** (25分): 检查是否包含配置文件
- **开发活跃度** (25分): 检查是否有提交历史

### 🔄 自动同步
- **定时更新**: 每6小时自动更新本地仓库
- **状态分析**: 定期分析项目状态并保存到数据库
- **手动触发**: 支持手动触发同步和分析

## 配置说明

### 环境变量

在 `backend/.env` 文件中添加以下配置：

```env
# 本地仓库配置
LOCAL_REPOS_DIR=/path/to/your/repos
```

### 数据库表结构

系统会自动创建 `project_statuses` 表，包含以下字段：

```sql
CREATE TABLE project_statuses (
    id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES projects(id) UNIQUE,
    has_readme BOOLEAN DEFAULT FALSE,
    readme_files TEXT[],
    total_files INTEGER DEFAULT 0,
    code_files INTEGER DEFAULT 0,
    doc_files INTEGER DEFAULT 0,
    config_files INTEGER DEFAULT 0,
    project_size_kb DECIMAL(10,2) DEFAULT 0,
    main_language VARCHAR(50),
    commit_count INTEGER DEFAULT 0,
    contributors INTEGER DEFAULT 0,
    last_commit TEXT,
    current_branch VARCHAR(100) DEFAULT 'main',
    has_package_json BOOLEAN DEFAULT FALSE,
    has_requirements_txt BOOLEAN DEFAULT FALSE,
    has_dockerfile BOOLEAN DEFAULT FALSE,
    quality_score INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## API接口

### 获取项目状态列表
```
GET /api/project-status/
```

### 获取单个项目状态
```
GET /api/project-status/{project_id}
```

### 获取项目状态总览
```
GET /api/project-status/summary/overview
```

### 手动触发项目分析
```
POST /api/project-status/analyze
```

### 更新本地仓库
```
POST /api/project-status/update-repos
```

### 手动执行完整同步
```
POST /api/project-status/sync
```

### 仅执行项目分析
```
POST /api/project-status/analysis-only
```

### 获取调度器状态
```
GET /api/project-status/scheduler/status
```

## 前端界面

### 项目状态总览页面
- **统计卡片**: 显示总项目数、README覆盖率、平均质量评分、平均提交次数
- **语言分布**: 显示各编程语言的项目分布
- **项目列表**: 以卡片形式展示每个项目的详细状态
- **操作按钮**: 支持手动更新仓库和分析项目

### 项目详情页面
- **基本信息**: 项目名称、GitHub链接、主要语言
- **状态指标**: README状态、文件统计、开发活跃度
- **质量评分**: 显示项目质量评分和建议
- **配置信息**: 显示项目配置文件状态

## 使用说明

### 1. 配置本地仓库目录
确保在环境变量中正确配置了 `LOCAL_REPOS_DIR`，该目录应包含所有项目的Git仓库。

### 2. 启动后端服务
```bash
cd backend
python main.py
```

系统启动时会自动：
- 初始化数据库表结构
- 启动后台调度器（每6小时同步一次）
- 首次分析所有项目状态

### 3. 访问前端界面
在浏览器中访问项目状态页面：
```
http://localhost:5173/project-status
```

### 4. 手动操作
- **更新仓库**: 点击"更新仓库"按钮手动更新所有本地仓库
- **分析项目**: 点击"分析项目"按钮手动触发项目状态分析
- **查看详情**: 点击项目卡片中的"查看详情"链接查看项目详细信息

## 定时任务

### 自动同步
- **频率**: 每6小时执行一次
- **内容**: 更新本地仓库 + 分析项目状态 + 保存到数据库
- **日志**: 记录在 `scheduler.log` 文件中

### 错误处理
- 如果同步失败，系统会等待1小时后重试
- 所有错误都会记录到日志文件中
- 可以通过API查看调度器状态

## 测试

运行测试脚本验证功能：
```bash
cd backend
python test_project_status.py
```

## 注意事项

1. **权限要求**: 确保系统有读取本地仓库目录的权限
2. **Git要求**: 确保系统已安装Git并可以执行git命令
3. **存储空间**: 项目分析会占用一定的CPU和内存资源
4. **网络连接**: 更新仓库需要网络连接
5. **数据库**: 确保PostgreSQL数据库正常运行

## 故障排除

### 常见问题

1. **本地仓库目录不存在**
   - 检查 `LOCAL_REPOS_DIR` 环境变量配置
   - 确保目录存在且有读取权限

2. **Git命令执行失败**
   - 检查Git是否已安装
   - 确保仓库目录包含有效的Git仓库

3. **数据库连接失败**
   - 检查数据库配置
   - 确保数据库服务正在运行

4. **分析结果不准确**
   - 检查本地仓库是否是最新版本
   - 手动触发仓库更新和分析

### 日志查看
- 应用日志: 查看控制台输出
- 调度器日志: 查看 `scheduler.log` 文件
- 数据库日志: 查看PostgreSQL日志 