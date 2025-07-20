# 项目进度跟踪功能说明

## 概述

项目进度跟踪功能是看板系统的新增功能，用于实时监控和分析所有项目在指定时间范围内的开发进度，包括提交活动、代码量变化、Issue活动等指标。

## 功能特性

### 📅 日历视图
- **项目活动日历**: 展示从2025年7月9日开始的5周内，每个项目在每一天的活动情况
- **提交指示器**: 显示每日提交数量，用不同颜色表示活跃程度
- **Issue活动**: 显示每日Issue创建和关闭情况
- **交互式选择**: 点击日期可查看详细的项目活动信息

### 📊 数据统计
- **总项目数**: 显示系统中跟踪的项目总数
- **活跃项目数**: 显示在跟踪期间有活动的项目数量
- **总提交数**: 显示所有项目的总提交次数
- **总Issue数**: 显示所有项目的总Issue数量

### 📈 图表分析
- **每日提交统计**: 柱状图显示每日提交数和活跃项目数
- **每日Issue活动**: 柱状图显示每日Issue创建和关闭情况
- **项目活跃度排名**: 显示项目按提交数排名的前10名

### 🏆 项目排名
- **活跃度排名**: 按总提交数、活跃天数等指标排名
- **详细统计**: 显示每个项目的提交数、代码行数、Issue活动等
- **进度条**: 可视化显示项目的活跃天数占比

## 数据来源

### Git提交数据
- 从本地Git仓库获取提交历史
- 统计每日提交数量、代码行数变化、文件变更数
- 支持增量同步，避免重复计算

### GitHub Issues数据
- 通过GitHub API获取Issues信息
- 统计Issue创建、关闭、评论等活动
- 实时同步最新的Issue状态

## 配置说明

### 环境变量

在 `backend/.env` 文件中确保以下配置：

```env
# 本地仓库配置
LOCAL_REPOS_DIR=/path/to/your/repos

# 数据库配置
DATABASE_URL=postgresql://username:password@localhost:5432/database_name
```

### 数据库表结构

系统会自动创建 `project_progress` 表，包含以下字段：

```sql
CREATE TABLE project_progress (
    id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES projects(id),
    date DATE NOT NULL,
    has_commit BOOLEAN DEFAULT FALSE,
    commit_count INTEGER DEFAULT 0,
    lines_added INTEGER DEFAULT 0,
    lines_deleted INTEGER DEFAULT 0,
    files_changed INTEGER DEFAULT 0,
    issues_created INTEGER DEFAULT 0,
    issues_closed INTEGER DEFAULT 0,
    issues_commented INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(project_id, date)
);
```

## API接口

### 获取进度摘要
```
GET /api/project-progress/summary
```

### 获取日历数据
```
GET /api/project-progress/calendar?start_date=2025-07-09&end_date=2025-08-13
```

### 获取单个项目进度
```
GET /api/project-progress/project/{project_id}
```

### 获取所有项目进度汇总
```
GET /api/project-progress/projects
```

### 手动触发同步
```
POST /api/project-progress/sync
```

## 同步程序

### 脚本位置
```
scripts/sync_project_progress.py
```

### 使用方法

1. **试运行模式**（不保存数据）：
```bash
python scripts/sync_project_progress.py --dry-run
```

2. **正常同步**：
```bash
python scripts/sync_project_progress.py
```

3. **同步指定项目**：
```bash
python scripts/sync_project_progress.py --project-id 1
```

### 同步流程

1. **获取项目列表**: 从数据库读取所有项目信息
2. **解析GitHub URL**: 提取owner/repo信息
3. **获取Git数据**: 从本地仓库读取提交历史
4. **获取Issues数据**: 通过GitHub API获取Issues信息
5. **数据聚合**: 按日期聚合提交和Issues数据
6. **保存到数据库**: 使用UPSERT操作保存进度数据

## 前端界面

### 项目进度页面
- **统计卡片**: 显示总项目数、活跃项目数、总提交数、总Issue数
- **图表展示**: 每日提交统计、Issue活动、项目排名图表
- **日历视图**: 交互式日历显示每日项目活动
- **项目排名**: 表格形式展示项目活跃度排名
- **同步按钮**: 手动触发数据同步

### 交互功能
- **日期选择**: 点击日历日期查看详细活动信息
- **项目链接**: 直接跳转到GitHub项目页面
- **数据刷新**: 支持手动同步和自动刷新

## 使用场景

### 教学管理
- 监控学生项目的开发进度
- 识别活跃和不活跃的项目
- 评估学生的参与度和贡献

### 项目评估
- 分析项目的开发节奏
- 评估代码质量和数量
- 跟踪Issue管理和解决情况

### 团队协作
- 了解团队成员的活跃度
- 识别需要关注的项目
- 优化开发流程和资源分配

## 注意事项

1. **数据同步**: 建议定期运行同步脚本以保持数据最新
2. **GitHub API限制**: 注意GitHub API的调用频率限制
3. **本地仓库**: 确保本地仓库路径正确且包含所有项目
4. **时间范围**: 默认跟踪从2025年7月9日开始的5周时间
5. **数据准确性**: 依赖Git提交历史和GitHub Issues数据

## 故障排除

### 常见问题

1. **同步失败**: 检查本地仓库路径和GitHub API权限
2. **数据不显示**: 确认数据库连接和表结构正确
3. **日历空白**: 检查日期范围和数据同步状态
4. **API错误**: 查看后端日志和网络连接状态

### 日志文件
- 同步日志: `logs/project_progress_sync.log`
- 后端日志: 查看FastAPI服务器日志
- 前端错误: 查看浏览器开发者工具控制台 