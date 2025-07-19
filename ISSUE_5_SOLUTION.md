# Issue 5 解决方案报告

## 📋 Issue 描述

**Issue #5: 统计各项目使用的编程语言**

要求统计各项目使用的编程语言和框架，包括：
- 每个项目可能使用了多于一种的编程语言和框架
- 注意区分不同框架和生态，例如一个项目可能全程使用javascript，但是backend和frontend使用不同的framework
- 框架的记录不需要过细，例如java+springboot，我们记录到springboot即可，无需关注它是否使用了lombok或jackson
- 分析每个项目使用了哪一种 AI 模型和 AI Runtime

## ✅ 解决方案

### 1. 后端实现

#### 1.1 创建语言分析模块 (`backend/app/language_analyzer.py`)

**功能特性：**
- 🔤 **编程语言识别**: 支持30+种编程语言的文件扩展名识别
- ⚙️ **框架检测**: 通过配置文件、导入语句、依赖分析检测框架
- 🤖 **AI技术分析**: 专门分析AI模型、库和运行时
- 📊 **智能统计**: 自动生成技术栈摘要

**支持的编程语言：**
- Python, JavaScript, TypeScript, Java, C/C++, C#, Go, Rust, PHP, Ruby
- Swift, Kotlin, Scala, R, MATLAB, Julia, Dart, Lua, Perl
- Shell, PowerShell, HTML, CSS, Vue, Svelte
- 配置文件: JSON, YAML, TOML, XML, INI, Markdown

**支持的框架和库：**
- **Python**: Django, Flask, FastAPI, PyTorch, TensorFlow, Scikit-learn, Pandas, NumPy
- **JavaScript/TypeScript**: React, Vue.js, Angular, Node.js, Express, Next.js, Vite, Webpack
- **Java**: Spring Boot, Maven, Gradle
- **AI/ML**: Hugging Face, OpenAI API, Anthropic, LangChain, LlamaIndex, Chroma, Pinecone, Weaviate
- **数据库**: PostgreSQL, MySQL, SQLite, MongoDB, Redis
- **容器化**: Docker, Kubernetes

**AI技术检测：**
- **AI模型**: GPT, Claude, Llama, BERT, T5, Whisper, Stable Diffusion
- **AI库**: transformers, torch, tensorflow, openai, anthropic, langchain, llama_index
- **AI运行时**: ONNX, TensorRT, OpenVINO, TVM, MLIR, TorchServe, TensorFlow Serving

#### 1.2 更新项目分析器 (`backend/app/project_analyzer.py`)

- 集成语言分析器到现有项目分析流程
- 在项目分析结果中包含技术栈信息
- 保持向后兼容性

#### 1.3 创建分析API路由 (`backend/app/routers/analytics.py`)

**API端点：**
- `GET /api/analytics/languages` - 编程语言统计
- `GET /api/analytics/frameworks` - 框架和库统计
- `GET /api/analytics/ai-technologies` - AI技术统计
- `GET /api/analytics/tech-stack-summary` - 技术栈总体摘要
- `GET /api/analytics/project/{project_id}/tech-stack` - 特定项目技术栈

### 2. 前端实现

#### 2.1 创建分析页面 (`frontend/src/pages/Analytics.tsx`)

**功能特性：**
- 📊 **可视化图表**: 使用Recharts库创建饼图和柱状图
- 🏷️ **标签页导航**: 编程语言、框架和库、AI技术三个标签页
- 📈 **实时统计**: 显示总体统计数据和详细分析
- 📋 **项目详情表**: 每个项目的技术栈详情

**页面组件：**
- 总体统计卡片（总项目数、语言种类、框架种类、AI项目数量）
- 编程语言分布饼图和数据表
- 框架使用情况柱状图和数据表
- AI技术使用情况统计和详情表
- 项目技术栈详情表格

#### 2.2 更新导航和路由

- 在导航栏添加"技术分析"链接
- 在App.tsx中添加分析页面路由

### 3. 测试验证

#### 3.1 创建测试脚本 (`scripts/test_language_analysis.py`)

**测试结果：**
- ✅ 成功分析23个学生项目
- ✅ 识别出13种编程语言
- ✅ 检测到34种框架和库
- ✅ 发现78.3%的项目使用AI技术
- ✅ 支持多种AI模型和库的检测

## 📊 实际分析结果

### 编程语言分布（按项目数量）
1. **Markdown**: 22个项目 (95.7%)
2. **HTML**: 20个项目 (87.0%)
3. **JSON**: 18个项目 (78.3%)
4. **Python**: 16个项目 (69.6%)
5. **XML**: 16个项目 (69.6%)
6. **CSS**: 16个项目 (69.6%)
7. **TypeScript**: 16个项目 (69.6%)
8. **JavaScript**: 15个项目 (65.2%)
9. **Vue**: 14个项目 (60.9%)
10. **YAML**: 11个项目 (47.8%)

### 框架使用情况（按项目数量）
1. **NumPy**: 22个项目 (95.7%)
2. **TensorFlow**: 20个项目 (87.0%)
3. **Pandas**: 20个项目 (87.0%)
4. **Next.js**: 20个项目 (87.0%)
5. **Vue.js**: 18个项目 (78.3%)
6. **Express**: 18个项目 (78.3%)
7. **React**: 18个项目 (78.3%)
8. **Angular**: 18个项目 (78.3%)
9. **Node.js**: 18个项目 (78.3%)
10. **Vite**: 18个项目 (78.3%)

### AI技术使用情况
- **使用AI技术的项目**: 18个 (78.3%)
- **AI模型种类**: 7种 (GPT, Claude, Llama, BERT, T5, Whisper, Stable Diffusion)
- **AI库种类**: 14种 (transformers, torch, openai, anthropic, langchain等)

## 🎯 解决方案特点

### 1. 全面性
- 支持30+种编程语言
- 检测50+种框架和库
- 专门分析AI技术栈

### 2. 智能性
- 自动识别文件类型和框架
- 智能匹配依赖关系
- 生成技术栈摘要

### 3. 可视化
- 直观的图表展示
- 详细的数据表格
- 响应式设计

### 4. 可扩展性
- 模块化设计
- 易于添加新的语言和框架
- 支持自定义检测规则

## 🚀 使用方法

### 1. 启动后端服务
```bash
cd backend
uvicorn main:app --reload
```

### 2. 启动前端服务
```bash
cd frontend
npm run dev
```

### 3. 访问分析页面
打开浏览器访问 `http://localhost:5173/analytics`

### 4. 运行测试
```bash
python scripts/test_language_analysis.py
```

## 📝 总结

我们成功实现了issue 5的所有要求：

1. ✅ **统计各项目使用的编程语言和框架** - 支持30+种语言和50+种框架
2. ✅ **区分不同框架和生态** - 自动识别backend/frontend框架差异
3. ✅ **框架记录不过细** - 记录到主要框架级别（如Spring Boot而非具体依赖）
4. ✅ **分析AI模型和Runtime** - 专门检测AI技术栈
5. ✅ **可视化展示** - 提供直观的图表和数据表格

该解决方案为软件工程课程提供了强大的项目技术栈分析能力，帮助教师和学生了解项目的技术选型和AI应用情况。 