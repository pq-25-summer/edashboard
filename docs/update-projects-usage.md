# 项目更新工具使用说明

## 概述

`update_projects.py` 是一个用于批量更新Git仓库项目的Python脚本。该脚本会递归查找指定目录下的所有Git仓库，并执行 `git pull` 来更新项目。

## 功能特性

- ✅ 递归查找所有包含 `.git` 目录的项目
- ✅ 自动检测仓库状态（clean/dirty）
- ✅ 智能跳过有未提交更改的仓库
- ✅ 支持强制更新模式
- ✅ 支持更新单个指定仓库
- ✅ 详细的日志记录和进度显示
- ✅ 显示当前分支和更新内容

## 使用方法

### 基本用法

```bash
# 更新指定目录下的所有Git仓库
python scripts/update_projects.py /path/to/repos

# 强制更新所有仓库（包括有未提交更改的）
python scripts/update_projects.py /path/to/repos --force

# 列出所有找到的Git仓库
python scripts/update_projects.py /path/to/repos --list

# 更新指定的单个仓库
python scripts/update_projects.py /path/to/repos --repo /path/to/specific/repo
```

### 参数说明

- `base_dir`: 必需参数，指定包含Git仓库的基础目录
- `--force`: 可选参数，强制更新，即使有未提交的更改
- `--list`: 可选参数，列出所有找到的Git仓库
- `--repo`: 可选参数，更新指定的单个仓库路径

### 示例

```bash
# 更新当前目录下的所有项目
python scripts/update_projects.py .

# 更新克隆的项目目录
python scripts/update_projects.py /Users/username/student-projects

# 强制更新所有项目
python scripts/update_projects.py ./repos --force

# 查看所有项目状态
python scripts/update_projects.py ./repos --list

# 更新特定项目
python scripts/update_projects.py ./repos --repo ./repos/ldg-aqing/llj-public
```

## 工作流程

### 1. 查找Git仓库
脚本会递归遍历指定目录，查找所有包含 `.git` 目录的文件夹：

```
base_dir/
├── owner1/
│   └── repo1/          # 包含 .git 目录
│       ├── .git/
│       └── src/
├── owner2/
│   └── repo2/          # 包含 .git 目录
│       ├── .git/
│       └── docs/
└── other_folder/       # 不包含 .git 目录
    └── files.txt
```

### 2. 检查仓库状态
对每个找到的Git仓库，脚本会：
- 检查当前分支
- 检查是否有未提交的更改
- 显示仓库状态（clean/dirty）

### 3. 执行更新
- 对于clean状态的仓库：直接执行 `git pull`
- 对于dirty状态的仓库：跳过更新（除非使用 `--force` 参数）

## 输出示例

### 列出仓库
```bash
$ python scripts/update_projects.py ./repos --list
2024-01-15 10:30:15 - INFO - 找到 23 个Git仓库:
 1. ldg-aqing/llj-public (分支: main, 状态: clean)
 2. TeamCvOriented/PQ-Project (分支: main, 状态: clean)
 3. kevinzhangzj710/popquiz-project (分支: master, 状态: dirty)
 4. sw-team-cosmogenesis/sw-project-PQ (分支: main, 状态: clean)
...
```

### 更新过程
```bash
$ python scripts/update_projects.py ./repos
2024-01-15 10:30:15 - INFO - 找到 23 个Git仓库
2024-01-15 10:30:15 - INFO - 开始更新 23 个仓库
2024-01-15 10:30:16 - INFO - 更新仓库: /path/to/repos/ldg-aqing/llj-public (分支: main)
2024-01-15 10:30:18 - INFO - 成功更新: /path/to/repos/ldg-aqing/llj-public
2024-01-15 10:30:18 - INFO - 更新内容: Already up to date.
2024-01-15 10:30:19 - WARNING - 仓库有未提交的更改，跳过: /path/to/repos/kevinzhangzj710/popquiz-project
2024-01-15 10:30:19 - WARNING - 状态: M  src/main.js
...
==================================================
更新完成摘要:
总仓库数: 23
成功更新: 20
失败数量: 3
成功率: 87.0%
基础目录: /path/to/repos
==================================================
```

## 错误处理

脚本包含完善的错误处理机制：

- **未提交更改**: 自动跳过有本地修改的仓库（除非使用 `--force`）
- **网络超时**: 单个仓库更新超时时间为5分钟
- **权限问题**: 记录错误信息并提供解决建议
- **无效仓库**: 跳过不是有效Git仓库的目录

## 安全特性

### 保护本地更改
默认情况下，脚本会保护本地未提交的更改：
- 检测到未提交更改时自动跳过
- 使用 `--force` 参数可以强制更新（谨慎使用）

### 状态检查
- 使用 `git status --porcelain` 检查仓库状态
- 显示当前分支信息
- 记录更新内容和结果

## 日志文件

脚本会生成详细的日志信息：

- **控制台输出**: 实时显示更新进度
- **日志文件**: `update_projects.log` 包含完整的操作记录
- **摘要报告**: 显示成功/失败统计

## 退出码

- `0`: 所有仓库更新成功
- `1`: 部分或全部仓库更新失败

## 注意事项

1. **网络连接**: 确保有稳定的网络连接访问远程仓库
2. **权限**: 确保对项目目录有读取和写入权限
3. **Git工具**: 确保系统已安装Git命令行工具
4. **本地更改**: 注意保护重要的本地更改

## 故障排除

### 常见问题

1. **更新失败**: 检查网络连接和远程仓库是否可访问
2. **权限错误**: 确保对项目目录有写入权限
3. **超时错误**: 网络较慢时可能需要更长的超时时间
4. **合并冲突**: 使用 `--force` 前请确保了解可能的风险

### 调试模式

可以通过查看日志文件 `update_projects.log` 获取详细的错误信息：

```bash
tail -f update_projects.log
```

## 最佳实践

1. **定期更新**: 建议定期运行更新脚本保持项目最新
2. **备份重要更改**: 在强制更新前备份重要的本地更改
3. **检查状态**: 使用 `--list` 参数定期检查项目状态
4. **选择性更新**: 使用 `--repo` 参数更新特定项目

## 扩展功能

脚本设计为可扩展的，未来可以添加：

- 并行更新支持
- 自定义更新策略
- 更多Git操作（fetch, rebase等）
- 通知和报告功能
- Kubernetes环境支持 