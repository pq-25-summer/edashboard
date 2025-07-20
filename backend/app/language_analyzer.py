"""
语言和框架分析模块
用于分析项目使用的编程语言、框架和AI技术
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Set, Optional
import logging


class LanguageAnalyzer:
    def __init__(self):
        self.setup_logging()
        
        # 编程语言映射
        self.language_extensions = {
            # 主要编程语言
            'Python': {'.py', '.pyx', '.pyi', '.pyw'},
            'JavaScript': {'.js', '.jsx', '.mjs'},
            'TypeScript': {'.ts', '.tsx'},
            'Java': {'.java', '.jav'},
            'C/C++': {'.c', '.cpp', '.cc', '.cxx', '.h', '.hpp', '.hxx'},
            'C#': {'.cs', '.csx'},
            'Go': {'.go'},
            'Rust': {'.rs'},
            'PHP': {'.php', '.phtml'},
            'Ruby': {'.rb', '.erb'},
            'Swift': {'.swift'},
            'Kotlin': {'.kt', '.kts'},
            'Scala': {'.scala', '.sc'},
            'R': {'.r', '.R'},
            'MATLAB': {'.m', '.mat'},
            'Julia': {'.jl'},
            'Dart': {'.dart'},
            'Lua': {'.lua'},
            'Perl': {'.pl', '.pm'},
            'Shell': {'.sh', '.bash', '.zsh', '.fish'},
            'PowerShell': {'.ps1', '.psm1'},
            
            # Web技术
            'HTML': {'.html', '.htm', '.xhtml'},
            'CSS': {'.css', '.scss', '.sass', '.less', '.styl'},
            'Vue': {'.vue'},
            'Svelte': {'.svelte'},
            
            # 配置文件
            'JSON': {'.json'},
            'YAML': {'.yaml', '.yml'},
            'TOML': {'.toml'},
            'XML': {'.xml'},
            'INI': {'.ini', '.cfg', '.conf'},
            'Markdown': {'.md', '.markdown'},
        }
        
        # 框架和库检测规则
        self.framework_patterns = {
            # Python框架
            'Django': {
                'files': ['manage.py', 'django-admin.py'],
                'imports': ['django', 'from django'],
                'requirements': ['django', 'Django']
            },
            'Flask': {
                'imports': ['flask', 'from flask'],
                'requirements': ['flask', 'Flask']
            },
            'FastAPI': {
                'imports': ['fastapi', 'from fastapi'],
                'requirements': ['fastapi', 'FastAPI']
            },
            'PyTorch': {
                'imports': ['torch', 'from torch'],
                'requirements': ['torch', 'PyTorch']
            },
            'TensorFlow': {
                'imports': ['tensorflow', 'tf', 'from tensorflow'],
                'requirements': ['tensorflow', 'TensorFlow']
            },
            'Scikit-learn': {
                'imports': ['sklearn', 'from sklearn'],
                'requirements': ['scikit-learn', 'sklearn']
            },
            'Pandas': {
                'imports': ['pandas', 'pd', 'from pandas'],
                'requirements': ['pandas', 'Pandas']
            },
            'NumPy': {
                'imports': ['numpy', 'np', 'from numpy'],
                'requirements': ['numpy', 'NumPy']
            },
            'OpenAI': {
                'imports': ['openai', 'from openai'],
                'requirements': ['openai', 'OpenAI']
            },
            'LangChain': {
                'imports': ['langchain', 'from langchain'],
                'requirements': ['langchain', 'LangChain']
            },
            'Transformers': {
                'imports': ['transformers', 'from transformers'],
                'requirements': ['transformers', 'Transformers']
            },
            
            # JavaScript/TypeScript框架
            'React': {
                'imports': ['react', 'from react', 'import React'],
                'dependencies': ['react', 'React'],
                'files': ['package.json']
            },
            'Vue.js': {
                'imports': ['vue', 'from vue', 'import Vue'],
                'dependencies': ['vue', 'Vue'],
                'files': ['package.json']
            },
            'Angular': {
                'imports': ['@angular', 'from @angular'],
                'dependencies': ['@angular/core', '@angular/common'],
                'files': ['package.json']
            },
            'Node.js': {
                'files': ['package.json', 'node_modules'],
                'dependencies': ['express', 'koa', 'fastify']
            },
            'Express': {
                'imports': ['express', 'from express'],
                'dependencies': ['express', 'Express'],
                'files': ['package.json']
            },
            'Next.js': {
                'imports': ['next', 'from next'],
                'dependencies': ['next', 'Next.js'],
                'files': ['package.json', 'next.config.js']
            },
            'Vite': {
                'dependencies': ['vite', 'Vite'],
                'files': ['package.json', 'vite.config.js', 'vite.config.ts']
            },
            'Webpack': {
                'dependencies': ['webpack', 'Webpack'],
                'files': ['package.json', 'webpack.config.js']
            },
            
            # Java框架
            'Spring Boot': {
                'files': ['pom.xml', 'build.gradle'],
                'dependencies': ['spring-boot-starter', 'spring-boot'],
                'imports': ['org.springframework', 'SpringBootApplication']
            },
            'Maven': {
                'files': ['pom.xml']
            },
            'Gradle': {
                'files': ['build.gradle', 'build.gradle.kts']
            },
            
            # AI/ML框架
            'Hugging Face': {
                'imports': ['transformers', 'datasets', 'tokenizers'],
                'requirements': ['transformers', 'datasets', 'tokenizers']
            },
            'OpenAI API': {
                'imports': ['openai', 'from openai'],
                'requirements': ['openai']
            },
            'Anthropic': {
                'imports': ['anthropic', 'from anthropic'],
                'requirements': ['anthropic']
            },
            'LlamaIndex': {
                'imports': ['llama_index', 'from llama_index'],
                'requirements': ['llama-index']
            },
            'Chroma': {
                'imports': ['chromadb', 'from chromadb'],
                'requirements': ['chromadb']
            },
            'Pinecone': {
                'imports': ['pinecone', 'from pinecone'],
                'requirements': ['pinecone-client']
            },
            'Weaviate': {
                'imports': ['weaviate', 'from weaviate'],
                'requirements': ['weaviate']
            },
            
            # 数据库
            'PostgreSQL': {
                'imports': ['psycopg', 'psycopg2', 'asyncpg'],
                'requirements': ['psycopg', 'psycopg2', 'asyncpg'],
                'dependencies': ['pg', 'postgres']
            },
            'MySQL': {
                'imports': ['mysql', 'pymysql', 'aiomysql'],
                'requirements': ['mysql-connector-python', 'pymysql', 'aiomysql']
            },
            'SQLite': {
                'imports': ['sqlite3', 'from sqlite3'],
                'files': ['.db', '.sqlite', '.sqlite3']
            },
            'MongoDB': {
                'imports': ['pymongo', 'motor', 'from pymongo'],
                'requirements': ['pymongo', 'motor'],
                'dependencies': ['mongodb', 'mongoose']
            },
            'Redis': {
                'imports': ['redis', 'aioredis', 'from redis'],
                'requirements': ['redis', 'aioredis'],
                'dependencies': ['redis', 'ioredis']
            },
            
            # 容器化
            'Docker': {
                'files': ['Dockerfile', 'docker-compose.yml', 'docker-compose.yaml', '.dockerignore']
            },
            'Kubernetes': {
                'files': ['.yaml', '.yml'],
                'patterns': [r'apiVersion:\s*v1', r'kind:\s*Deployment', r'kind:\s*Service']
            }
        }
        
        # AI模型和Runtime检测
        self.ai_patterns = {
            'GPT': {
                'patterns': [r'gpt-\d+', r'gpt\d+', r'GPT-\d+', r'GPT\d+'],
                'imports': ['openai', 'from openai'],
                'requirements': ['openai']
            },
            'Claude': {
                'patterns': [r'claude-\d+', r'claude\d+', r'Claude-\d+', r'Claude\d+'],
                'imports': ['anthropic', 'from anthropic'],
                'requirements': ['anthropic']
            },
            'Llama': {
                'patterns': [r'llama-\d+', r'llama\d+', r'Llama-\d+', r'Llama\d+'],
                'imports': ['transformers', 'llama_index'],
                'requirements': ['transformers', 'llama-index']
            },
            'BERT': {
                'patterns': [r'bert', r'BERT'],
                'imports': ['transformers', 'from transformers'],
                'requirements': ['transformers']
            },
            'T5': {
                'patterns': [r't5', r'T5'],
                'imports': ['transformers'],
                'requirements': ['transformers']
            },
            'Whisper': {
                'patterns': [r'whisper', r'Whisper'],
                'imports': ['openai', 'whisper'],
                'requirements': ['openai-whisper', 'whisper']
            },
            'Stable Diffusion': {
                'patterns': [r'stable-diffusion', r'Stable Diffusion'],
                'imports': ['diffusers', 'transformers'],
                'requirements': ['diffusers', 'transformers']
            }
        }
    
    def setup_logging(self):
        """设置日志"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def analyze_project_languages(self, repo_path: Path) -> Dict:
        """分析项目使用的编程语言"""
        languages = {}
        
        try:
            for file_path in repo_path.rglob('*'):
                if file_path.is_file() and '.git' not in str(file_path):
                    ext = file_path.suffix.lower()
                    
                    # 根据文件扩展名识别语言
                    for lang, extensions in self.language_extensions.items():
                        if ext in extensions:
                            languages[lang] = languages.get(lang, 0) + 1
                            break
            
            # 按文件数量排序
            languages = dict(sorted(languages.items(), key=lambda x: x[1], reverse=True))
            
        except Exception as e:
            self.logger.error(f"分析编程语言失败 {repo_path}: {e}")
        
        return languages
    
    def analyze_project_frameworks(self, repo_path: Path) -> Dict:
        """分析项目使用的框架和库"""
        frameworks = {}
        
        try:
            # 分析package.json (Node.js项目)
            package_json = repo_path / 'package.json'
            if package_json.exists():
                try:
                    with open(package_json, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        
                    # 检查dependencies和devDependencies
                    deps = data.get('dependencies', {})
                    dev_deps = data.get('devDependencies', {})
                    all_deps = {**deps, **dev_deps}
                    
                    for dep_name in all_deps.keys():
                        for framework, patterns in self.framework_patterns.items():
                            if 'dependencies' in patterns:
                                for pattern in patterns['dependencies']:
                                    if pattern.lower() in dep_name.lower():
                                        frameworks[framework] = frameworks.get(framework, 0) + 1
                                        break
                except Exception as e:
                    self.logger.warning(f"解析package.json失败: {e}")
            
            # 分析requirements.txt (Python项目)
            requirements_files = ['requirements.txt', 'requirements-dev.txt', 'pyproject.toml']
            for req_file in requirements_files:
                req_path = repo_path / req_file
                if req_path.exists():
                    try:
                        with open(req_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            
                        for framework, patterns in self.framework_patterns.items():
                            if 'requirements' in patterns:
                                for pattern in patterns['requirements']:
                                    if pattern.lower() in content.lower():
                                        frameworks[framework] = frameworks.get(framework, 0) + 1
                                        break
                    except Exception as e:
                        self.logger.warning(f"解析{req_file}失败: {e}")
            
            # 分析pom.xml (Java Maven项目)
            pom_xml = repo_path / 'pom.xml'
            if pom_xml.exists():
                try:
                    with open(pom_xml, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                    for framework, patterns in self.framework_patterns.items():
                        if 'dependencies' in patterns:
                            for pattern in patterns['dependencies']:
                                if pattern.lower() in content.lower():
                                    frameworks[framework] = frameworks.get(framework, 0) + 1
                                    break
                except Exception as e:
                    self.logger.warning(f"解析pom.xml失败: {e}")
            
            # 分析代码文件中的导入语句
            code_files = ['.py', '.js', '.ts', '.jsx', '.tsx', '.java']
            for file_path in repo_path.rglob('*'):
                if file_path.is_file() and file_path.suffix.lower() in code_files:
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            
                        for framework, patterns in self.framework_patterns.items():
                            if 'imports' in patterns:
                                for pattern in patterns['imports']:
                                    if pattern.lower() in content.lower():
                                        frameworks[framework] = frameworks.get(framework, 0) + 1
                                        break
                    except Exception:
                        # 忽略无法读取的文件
                        pass
            
            # 检查特殊文件
            for file_path in repo_path.rglob('*'):
                if file_path.is_file():
                    for framework, patterns in self.framework_patterns.items():
                        if 'files' in patterns:
                            for pattern in patterns['files']:
                                if pattern in file_path.name:
                                    frameworks[framework] = frameworks.get(framework, 0) + 1
                                    break
            
        except Exception as e:
            self.logger.error(f"分析框架失败 {repo_path}: {e}")
        
        return frameworks
    
    def analyze_ai_technologies(self, repo_path: Path) -> Dict:
        """分析项目使用的AI技术"""
        ai_tech = {
            'models': [],
            'runtimes': [],
            'libraries': []
        }
        
        try:
            # 分析所有文本文件
            text_extensions = {'.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.md', '.txt', '.json', '.yaml', '.yml'}
            
            for file_path in repo_path.rglob('*'):
                if file_path.is_file() and file_path.suffix.lower() in text_extensions:
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            
                        # 检查AI模型
                        for model, patterns in self.ai_patterns.items():
                            if 'patterns' in patterns:
                                for pattern in patterns['patterns']:
                                    if re.search(pattern, content, re.IGNORECASE):
                                        if model not in ai_tech['models']:
                                            ai_tech['models'].append(model)
                                        break
                            
                            if 'imports' in patterns:
                                for pattern in patterns['imports']:
                                    if pattern.lower() in content.lower():
                                        if model not in ai_tech['models']:
                                            ai_tech['models'].append(model)
                                        break
                        
                        # 检查AI运行时和库
                        ai_libraries = [
                            'openai', 'anthropic', 'transformers', 'torch', 'tensorflow',
                            'langchain', 'llama_index', 'chromadb', 'pinecone', 'weaviate',
                            'sentence-transformers', 'spacy', 'nltk', 'gensim'
                        ]
                        
                        for lib in ai_libraries:
                            if lib.lower() in content.lower():
                                if lib not in ai_tech['libraries']:
                                    ai_tech['libraries'].append(lib)
                        
                        # 检查AI运行时
                        ai_runtimes = [
                            'onnx', 'tensorrt', 'openvino', 'tvm', 'mlir',
                            'torchserve', 'tensorflow-serving', 'bentoml', 'seldon'
                        ]
                        
                        for runtime in ai_runtimes:
                            if runtime.lower() in content.lower():
                                if runtime not in ai_tech['runtimes']:
                                    ai_tech['runtimes'].append(runtime)
                                    
                    except Exception:
                        # 忽略无法读取的文件
                        pass
            
            # 检查requirements.txt和package.json中的AI库
            requirements_files = ['requirements.txt', 'pyproject.toml', 'package.json']
            for req_file in requirements_files:
                req_path = repo_path / req_file
                if req_path.exists():
                    try:
                        with open(req_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            
                        for lib in ai_tech['libraries']:
                            if lib.lower() in content.lower():
                                if lib not in ai_tech['libraries']:
                                    ai_tech['libraries'].append(lib)
                    except Exception:
                        pass
            
        except Exception as e:
            self.logger.error(f"分析AI技术失败 {repo_path}: {e}")
        
        return ai_tech
    
    def analyze_project_tech_stack(self, repo_path: Path) -> Dict:
        """综合分析项目的技术栈"""
        analysis = {
            'languages': self.analyze_project_languages(repo_path),
            'frameworks': self.analyze_project_frameworks(repo_path),
            'ai_technologies': self.analyze_ai_technologies(repo_path),
            'summary': {}
        }
        
        # 生成技术栈摘要
        if analysis['languages']:
            analysis['summary']['primary_language'] = list(analysis['languages'].keys())[0]
            analysis['summary']['language_count'] = len(analysis['languages'])
        
        if analysis['frameworks']:
            analysis['summary']['framework_count'] = len(analysis['frameworks'])
            analysis['summary']['main_frameworks'] = list(analysis['frameworks'].keys())[:5]
        
        if analysis['ai_technologies']['models'] or analysis['ai_technologies']['libraries']:
            analysis['summary']['has_ai'] = True
            analysis['summary']['ai_models'] = analysis['ai_technologies']['models']
            analysis['summary']['ai_libraries'] = analysis['ai_technologies']['libraries']
        else:
            analysis['summary']['has_ai'] = False
        
        return analysis 