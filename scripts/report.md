# GitHub Issue 数据抓取报告

## 概述
成功从 GitHub Issue https://github.com/xinase/PQ/issues/3 抓取了项目和学生信息。

## 数据统计
- **项目数量**: 24个
- **学生数量**: 80个
- **抓取时间**: 2024年12月

## 数据格式

### 项目文件 (projects.txt)
格式：`项目名称\tGitHub仓库URL`
```
PQ-Project	https://github.com/Liangyu-Sun
popquiz-project	https://github.com/3241672910
sw-project-PQ	https://github.com/zhangN247
...
```

### 学生文件 (students.txt)
格式：`学生姓名\tGitHub用户名\tGitHub个人主页URL`
```
何佳骏	waitlili414	https://github.com/waitlili414
俞俊杉	Yujunshan	https://github.com/Yujunshan
修嘉成	XX1012955	https://github.com/XX1012955
...
```

## 项目列表
1. **llj-public** - 3名学生
2. **PQ-Project** - 3名学生  
3. **popquiz-project** - 3名学生
4. **sw-project-PQ** - 4名学生
5. **project_1** - 4名学生
6. **sw-project-demo** - 3名学生
7. **ai-question** - 3名学生
8. **kbdui-work** - 4名学生
9. **quizgen** - 4名学生
10. **qwer111** - 3名学生
11. **project** - 3名学生
12. **AI-quiz** - 3名学生
13. **demo-proj1** - 3名学生
14. **RainbowTeam** - 4名学生
15. **sw-project-demo** - 4名学生
16. **PQ_LTeamProject** - 3名学生
17. **PopQuiz** - 3名学生
18. **MSN-Homework** - 3名学生
19. **PQ_repo** - 3名学生
20. **PQ-project** - 3名学生
21. **internship203** - 4名学生
22. **Oblivionis1** - 3名学生
23. **summer-project** - 4名学生
24. **ConnectWork** - 3名学生

## 技术实现
- 使用 `httpx` 库进行HTTP请求
- 解析GitHub Issue的markdown表格格式
- 自动提取学生姓名、GitHub用户名和个人主页链接
- 支持去重和错误处理

## 数据质量
- ✅ 成功提取所有学生的姓名
- ✅ 成功提取所有学生的GitHub用户名
- ✅ 成功生成所有学生的GitHub个人主页链接
- ✅ 项目名称使用GitHub仓库名（更准确）
- ✅ 数据已按姓名排序

## 注意事项
- 部分学生的GitHub用户名可能与姓名不完全匹配
- 所有GitHub链接都已验证格式正确
- 数据已去重，避免重复记录 