# GitHub Issue 数据抓取脚本

## 功能说明

从指定的GitHub Issue中抓取项目列表和学生信息，包括：
- 项目名称和GitHub仓库链接
- 学生姓名、GitHub用户名和个人主页链接

## 目标Issue

https://github.com/xinase/PQ/issues/3

## 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

### 基本使用
```bash
python get_repos.py
```

### 使用GitHub Token（推荐）
```bash
export GITHUB_TOKEN=your_token_here
python get_repos.py
```

## 输出文件

### projects.txt
项目列表文件，格式：`项目名称\tGitHub仓库URL`
```
PQ-Project	https://github.com/Liangyu-Sun
popquiz-project	https://github.com/3241672910
sw-project-PQ	https://github.com/zhangN247
...
```

### students.txt
学生列表文件，格式：`学生姓名\tGitHub用户名\tGitHub个人主页URL`
```
何佳骏	waitlili414	https://github.com/waitlili414
俞俊杉	Yujunshan	https://github.com/Yujunshan
修嘉成	XX1012955	https://github.com/XX1012955
...
```

## 数据统计

- **项目数量**: 24个
- **学生数量**: 80个
- **数据来源**: GitHub Issue #3 及其评论

## 技术特点

- 使用GitHub API，遵循官方使用规范
- 智能解析Markdown表格格式
- 自动提取学生GitHub信息
- 支持数据去重和错误处理
- 生成完整的GitHub个人主页链接

## 调试工具

### debug_issue.py
用于调试和查看原始Issue内容：
```bash
python debug_issue.py
```

生成文件：
- `issue_content.txt` - 原始Issue内容
- `issue_comments.txt` - 原始评论内容

## 注意事项

1. **GitHub Token**: 建议使用GitHub Token以提高API限制配额
2. **网络连接**: 需要稳定的网络连接访问GitHub API
3. **数据格式**: 脚本会自动处理Markdown格式和特殊字符
4. **去重处理**: 相同姓名的学生会被去重，保留最完整的GitHub信息

## 错误处理

脚本包含完善的错误处理机制：
- 网络连接失败
- API限制超限
- 数据格式异常
- 文件写入错误

## 更新日志

### v2.2 (当前版本)
- ✅ 新增项目更新脚本 `update_projects.py`
- ✅ 支持批量更新所有Git仓库
- ✅ 智能检测仓库状态和分支信息
- ✅ 保护本地未提交更改
- ✅ 支持强制更新和选择性更新

### v2.1
- ✅ 新增项目克隆脚本 `clone_all.py`
- ✅ 支持批量克隆所有学员项目
- ✅ 自动创建 owner/repo 目录结构
- ✅ 完善的错误处理和日志记录

### v2.0
- ✅ 新增学生GitHub用户名和个人主页链接
- ✅ 改进数据结构和输出格式
- ✅ 增强错误处理和数据验证
- ✅ 优化去重逻辑

### v1.0
- ✅ 基础项目和学生信息抓取
- ✅ GitHub API集成
- ✅ Markdown表格解析

## 项目克隆

### 克隆脚本
使用 `clone_all.py` 批量克隆所有学员项目：
```bash
# 克隆到指定目录
python clone_all.py /path/to/repos

# 使用自定义项目文件
python clone_all.py /path/to/repos --projects-file custom_projects.txt
```

### 功能特点
- ✅ 支持命令行参数指定目标目录
- ✅ 自动创建 `owner/repo` 目录结构避免同名冲突
- ✅ 详细的日志记录和进度显示
- ✅ 跳过已存在的项目目录
- ✅ 错误处理和超时控制

### 使用说明
详细使用说明请查看: [docs/clone-all-usage.md](../docs/clone-all-usage.md)

## 项目更新

### 更新脚本
使用 `update_projects.py` 批量更新所有Git仓库：
```bash
# 更新所有仓库
python update_projects.py /path/to/repos

# 强制更新（包括有未提交更改的）
python update_projects.py /path/to/repos --force

# 列出所有找到的Git仓库
python update_projects.py /path/to/repos --list

# 更新指定仓库
python update_projects.py /path/to/repos --repo /path/to/specific/repo
```

### 功能特点
- ✅ 递归查找所有包含 `.git` 目录的项目
- ✅ 自动检测仓库状态（clean/dirty）
- ✅ 智能跳过有未提交更改的仓库
- ✅ 支持强制更新模式
- ✅ 支持更新单个指定仓库
- ✅ 显示当前分支和更新内容

### 使用说明
详细使用说明请查看: [docs/update-projects-usage.md](../docs/update-projects-usage.md)

## 数据同步

### 同步脚本
使用 `sync_data.py` 将抓取的数据同步到数据库：
```bash
# 预览模式
python sync_data.py --dry-run

# 实际同步
python sync_data.py
```

### 同步状态
- ✅ **2024-12-18**: 成功同步24个项目和80个学生到开发服务器
- 📊 **数据验证**: 通过API确认所有数据已正确导入
- 🔗 **关联状态**: 学生-项目关联需要手动设置

### 同步报告
详细报告请查看: [sync_report.md](sync_report.md) 