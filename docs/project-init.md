# 软件工程课看板

我们需要开发一个看板系统，用于分析和查看学员们的学习情况。

## 背景和假设

课程的形式是建立一个github public项目，然后所有的学员分组，复制并建立自己的github public项目，在各自小组的项目中完成这个软件工程项目。我们通过分析各个小组的进度，学员们的代码提交、issue、文档等工作来评估工作的贡献和质量。

因此，我们需要一个web项目，能够抓取配置的项目状态，分析数据。这需要调用 github 的 api，也需要一些基于git的操作。

## 技术架构

主要工具链如下：
- python
- psycopg 需要注意的是这里使用 psycopg，当前这个项目对应 psycopg3 ，它不是 psycopg2
- pydantic
- fastapi
- react
- react-bootstrap
- echarts-for-react
- typescript
- vite
- postgresql
- 我们还需要用 k8s 而非 docker-compose 管理实例，以便编排定时同步github和dashboard状态的任务

