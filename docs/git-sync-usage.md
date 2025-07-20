# Git同步功能使用说明

## 📋 概述

为了提高系统性能和可维护性，我们将Git仓库同步操作从分析任务中分离出来，创建了独立的Git同步程序。这样可以避免分析任务被git操作阻塞，提高系统的响应性。

## 🏗️ 架构设计

### 1. 分离的职责

- **Git同步程序** (`scripts/git_sync.py`): 专门负责更新所有本地仓库
- **项目分析程序** (`scripts/analyze_projects.py`): 专注于分析项目状态和技术栈
- **技术栈保存程序** (`scripts/save_tech_stack.py`): 专门保存技术栈数据到数据库

### 2. 工作流程

```
Git同步 → 项目分析 → 技术栈分析 → 数据保存
   ↓         ↓           ↓           ↓
独立程序   独立程序     独立程序     独立程序
```

## 🚀 使用方法

### 1. 使用CLI工具（推荐）

```bash
# 同步Git仓库
python scripts/cli.py git-sync

# 分析项目状态
python scripts/cli.py analyze

# 保存技术栈数据
python scripts/cli.py tech-stack

# 查看系统状态
python scripts/cli.py status

# 执行完整数据同步
python scripts/cli.py sync
```

### 2. 直接运行脚本

```bash
# Git同步
python scripts/git_sync.py

# 项目分析
python scripts/analyze_projects.py

# 技术栈保存
python scripts/save_tech_stack.py
```

## 📊 功能特性

### Git同步程序 (`git_sync.py`)

**功能：**
- 🔄 自动同步所有本地Git仓库
- 📊 检查仓库更新状态
- 🛡️ 安全处理未提交的更改
- 📝 记录同步日志到数据库
- ⚡ 异步处理，提高效率

**特性：**
- 智能检测是否需要更新
- 避免覆盖本地更改
- 详细的同步统计
- 错误处理和日志记录

**输出示例：**
```
📊 同步摘要:
   - 总项目数: 24
   - 同步成功: 22
   - 同步失败: 2
   - 有更新: 1
   - 耗时: 0:00:38.039976

🔄 建议: 有 1 个项目有更新，可以运行分析任务
```

### 项目分析程序 (`analyze_projects.py`)

**功能：**
- 📁 分析项目文件结构
- 📊 计算项目质量评分
- 🔍 检测README、配置文件等
- 💾 保存分析结果到数据库

### 技术栈保存程序 (`save_tech_stack.py`)

**功能：**
- 🔤 分析编程语言使用情况
- ⚙️ 检测框架和库
- 🤖 识别AI技术栈
- 📊 生成技术栈统计

## 🔧 配置说明

### 1. 数据库表结构

**Git同步日志表 (`git_sync_logs`)：**
```sql
CREATE TABLE git_sync_logs (
    id SERIAL PRIMARY KEY,
    sync_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_projects INTEGER,
    successful_syncs INTEGER,
    failed_syncs INTEGER,
    projects_with_changes INTEGER,
    sync_duration_seconds DECIMAL(10,2),
    details JSONB
);
```

**项目技术栈表 (`project_tech_stacks`)：**
```sql
CREATE TABLE project_tech_stacks (
    id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES projects(id) UNIQUE,
    languages JSONB,
    frameworks JSONB,
    ai_models JSONB,
    ai_libraries JSONB,
    ai_runtimes JSONB,
    total_languages INTEGER DEFAULT 0,
    total_frameworks INTEGER DEFAULT 0,
    total_ai_models INTEGER DEFAULT 0,
    total_ai_libraries INTEGER DEFAULT 0,
    has_ai BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 2. 配置文件

确保 `backend/app/config.py` 中的配置正确：
```python
# 本地仓库目录
local_repos_dir: str = "/Users/mars/jobs/pq/repos"

# 数据库连接
database_url: str = "postgresql://localhost/edashboard"
```

## 📈 性能优化

### 1. 异步处理
- 所有Git操作都使用异步处理
- 避免阻塞主线程
- 提高并发性能

### 2. 智能更新检测
- 只更新有变化的仓库
- 避免不必要的git pull操作
- 减少网络请求

### 3. 错误处理
- 完善的异常处理机制
- 详细的错误日志
- 失败重试机制

## 🛠️ 故障排除

### 1. 常见问题

**问题：仓库有未提交的更改**
```
解决方案：手动处理本地更改，或使用git stash
```

**问题：网络连接失败**
```
解决方案：检查网络连接，重试同步操作
```

**问题：权限不足**
```
解决方案：检查Git仓库的访问权限
```

### 2. 日志查看

```bash
# 查看Git同步日志
tail -f logs/git_sync.log

# 查看CLI日志
tail -f cli.log
```

## 🔄 定时任务

### 1. 使用cron（Linux/macOS）

```bash
# 编辑crontab
crontab -e

# 添加定时任务（每小时同步一次）
0 * * * * cd /path/to/edashboard && python scripts/cli.py git-sync

# 每天凌晨2点执行完整分析
0 2 * * * cd /path/to/edashboard && python scripts/cli.py analyze
```

### 2. 使用systemd（Linux）

创建服务文件 `/etc/systemd/system/git-sync.service`：
```ini
[Unit]
Description=Git Sync Service
After=network.target

[Service]
Type=oneshot
User=your-user
WorkingDirectory=/path/to/edashboard
ExecStart=/usr/bin/python3 scripts/git_sync.py

[Install]
WantedBy=multi-user.target
```

创建定时器文件 `/etc/systemd/system/git-sync.timer`：
```ini
[Unit]
Description=Run Git Sync every hour
Requires=git-sync.service

[Timer]
OnCalendar=hourly
Persistent=true

[Install]
WantedBy=timers.target
```

## 📝 总结

通过将Git同步操作分离到独立程序，我们实现了：

1. ✅ **性能提升**: 分析任务不再被git操作阻塞
2. ✅ **职责分离**: 每个程序专注于特定功能
3. ✅ **可维护性**: 更容易调试和维护
4. ✅ **可扩展性**: 可以独立优化每个组件
5. ✅ **监控能力**: 详细的日志和统计信息

这种设计使得系统更加稳定和高效，同时提供了更好的用户体验。 