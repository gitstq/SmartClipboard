"""
AI处理模块 - 提供智能文本处理能力
"""

import os
import re
import json
from typing import Optional, Dict, List, Callable
from dataclasses import dataclass
from enum import Enum
import threading


class AIFeature(Enum):
    """AI功能枚举"""
    SUMMARIZE = "summarize"          # 文本摘要
    TRANSLATE = "translate"          # 翻译
    FORMAT = "format"                # 格式化
    EXTRACT = "extract"              # 信息提取
    GENERATE = "generate"            # 内容生成
    CODE_REVIEW = "code_review"      # 代码审查
    SENTIMENT = "sentiment"          # 情感分析
    CLASSIFY = "classify"            # 分类


@dataclass
class AIResult:
    """AI处理结果"""
    success: bool
    content: str
    feature: AIFeature
    error: str = ""
    metadata: Dict = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class AIProcessor:
    """AI处理器 - 支持多种AI后端"""
    
    def __init__(self, api_key: Optional[str] = None, provider: str = "openai"):
        """初始化AI处理器
        
        Args:
            api_key: API密钥
            provider: AI提供商 (openai, anthropic, local)
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
        self.provider = provider
        self._client = None
        self._initialized = False
        self._lock = threading.Lock()
        
        # 初始化客户端
        self._init_client()
    
    def _init_client(self):
        """初始化AI客户端"""
        try:
            if self.provider == "openai":
                self._init_openai()
            elif self.provider == "anthropic":
                self._init_anthropic()
            elif self.provider == "local":
                self._init_local()
        except Exception as e:
            print(f"AI client initialization failed: {e}")
            self._initialized = False
    
    def _init_openai(self):
        """初始化OpenAI客户端"""
        try:
            import openai
            if self.api_key:
                self._client = openai.OpenAI(api_key=self.api_key)
                self._initialized = True
                print("OpenAI client initialized")
        except ImportError:
            print("OpenAI package not installed")
    
    def _init_anthropic(self):
        """初始化Anthropic客户端"""
        try:
            import anthropic
            if self.api_key:
                self._client = anthropic.Anthropic(api_key=self.api_key)
                self._initialized = True
                print("Anthropic client initialized")
        except ImportError:
            print("Anthropic package not installed")
    
    def _init_local(self):
        """初始化本地模型"""
        # 本地模型支持（如Ollama）
        self._initialized = False
        print("Local AI not implemented yet")
    
    def is_available(self) -> bool:
        """检查AI是否可用"""
        return self._initialized
    
    def process(self, text: str, feature: AIFeature, **kwargs) -> AIResult:
        """处理文本
        
        Args:
            text: 输入文本
            feature: 处理功能
            **kwargs: 额外参数
            
        Returns:
            AI处理结果
        """
        if not self._initialized:
            return AIResult(
                success=False,
                content="",
                feature=feature,
                error="AI client not initialized"
            )
        
        # 构建提示词
        prompt = self._build_prompt(text, feature, **kwargs)
        
        try:
            if self.provider == "openai":
                return self._call_openai(prompt, feature)
            elif self.provider == "anthropic":
                return self._call_anthropic(prompt, feature)
            else:
                return AIResult(
                    success=False,
                    content="",
                    feature=feature,
                    error="Unknown provider"
                )
        except Exception as e:
            return AIResult(
                success=False,
                content="",
                feature=feature,
                error=str(e)
            )
    
    def _build_prompt(self, text: str, feature: AIFeature, **kwargs) -> str:
        """构建提示词"""
        prompts = {
            AIFeature.SUMMARIZE: f"""请对以下文本进行摘要，提取关键信息：

{text}

要求：
1. 保持原文的核心意思
2. 摘要长度控制在100字以内
3. 使用简洁的语言

摘要：""",
            
            AIFeature.TRANSLATE: f"""请将以下文本翻译成{kwargs.get('target_lang', '中文')}：

{text}

翻译：""",
            
            AIFeature.FORMAT: f"""请对以下文本进行格式化整理：

{text}

要求：
1. 修正错别字和语法错误
2. 优化段落结构
3. 统一标点符号使用

格式化后的文本：""",
            
            AIFeature.EXTRACT: f"""请从以下文本中提取{kwargs.get('extract_type', '关键信息')}：

{text}

提取结果：""",
            
            AIFeature.CODE_REVIEW: f"""请对以下代码进行审查：

{text}

审查要点：
1. 代码质量和可读性
2. 潜在的错误或漏洞
3. 性能优化建议
4. 最佳实践建议

审查结果：""",
            
            AIFeature.SENTIMENT: f"""请分析以下文本的情感倾向：

{text}

请输出：
1. 情感类型（正面/负面/中性）
2. 情感强度（0-1）
3. 简要分析

分析结果：""",
            
            AIFeature.CLASSIFY: f"""请将以下文本分类：

{text}

可选类别：{kwargs.get('categories', '工作,生活,学习,娱乐,其他')}

分类结果：""",
            
            AIFeature.GENERATE: f"""请根据以下要求生成内容：

{text}

生成的内容："""
        }
        
        return prompts.get(feature, text)
    
    def _call_openai(self, prompt: str, feature: AIFeature) -> AIResult:
        """调用OpenAI API"""
        try:
            response = self._client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "你是一个专业的文本处理助手。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            content = response.choices[0].message.content
            
            return AIResult(
                success=True,
                content=content.strip(),
                feature=feature,
                metadata={
                    "model": response.model,
                    "tokens": response.usage.total_tokens if response.usage else 0
                }
            )
        except Exception as e:
            return AIResult(
                success=False,
                content="",
                feature=feature,
                error=f"OpenAI API error: {str(e)}"
            )
    
    def _call_anthropic(self, prompt: str, feature: AIFeature) -> AIResult:
        """调用Anthropic API"""
        try:
            response = self._client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=1000,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            content = response.content[0].text if response.content else ""
            
            return AIResult(
                success=True,
                content=content.strip(),
                feature=feature,
                metadata={
                    "model": response.model,
                    "tokens": response.usage.input_tokens + response.usage.output_tokens if response.usage else 0
                }
            )
        except Exception as e:
            return AIResult(
                success=False,
                content="",
                feature=feature,
                error=f"Anthropic API error: {str(e)}"
            )
    
    # 便捷方法
    def summarize(self, text: str, max_length: int = 100) -> AIResult:
        """文本摘要"""
        return self.process(text, AIFeature.SUMMARIZE, max_length=max_length)
    
    def translate(self, text: str, target_lang: str = "中文") -> AIResult:
        """翻译文本"""
        return self.process(text, AIFeature.TRANSLATE, target_lang=target_lang)
    
    def format_text(self, text: str) -> AIResult:
        """格式化文本"""
        return self.process(text, AIFeature.FORMAT)
    
    def extract_info(self, text: str, extract_type: str = "关键信息") -> AIResult:
        """提取信息"""
        return self.process(text, AIFeature.EXTRACT, extract_type=extract_type)
    
    def review_code(self, code: str) -> AIResult:
        """代码审查"""
        return self.process(code, AIFeature.CODE_REVIEW)
    
    def analyze_sentiment(self, text: str) -> AIResult:
        """情感分析"""
        return self.process(text, AIFeature.SENTIMENT)
    
    def classify(self, text: str, categories: str = "工作,生活,学习,娱乐,其他") -> AIResult:
        """文本分类"""
        return self.process(text, AIFeature.CLASSIFY, categories=categories)


class LocalAIProcessor:
    """本地AI处理器 - 无需API密钥的基础文本处理"""
    
    def __init__(self):
        self._initialized = True
    
    def is_available(self) -> bool:
        return True
    
    def summarize(self, text: str, max_length: int = 100) -> AIResult:
        """简单的文本摘要 - 提取前N个字符"""
        sentences = re.split(r'[。！？.!?]', text)
        summary = ""
        for sent in sentences[:3]:  # 取前3句
            if len(summary) + len(sent) < max_length:
                summary += sent + "。"
            else:
                break
        
        return AIResult(
            success=True,
            content=summary or text[:max_length] + "...",
            feature=AIFeature.SUMMARIZE,
            metadata={"method": "extractive"}
        )
    
    def format_text(self, text: str) -> AIResult:
        """基础文本格式化"""
        # 去除多余空格
        formatted = re.sub(r'\s+', ' ', text)
        # 去除多余换行
        formatted = re.sub(r'\n\s*\n', '\n\n', formatted)
        # 去除首尾空白
        formatted = formatted.strip()
        
        return AIResult(
            success=True,
            content=formatted,
            feature=AIFeature.FORMAT,
            metadata={"method": "rule_based"}
        )
    
    def classify(self, text: str, categories: str = "工作,生活,学习,娱乐,其他") -> AIResult:
        """基于关键词的简单分类"""
        keywords = {
            "工作": ["会议", "项目", "邮件", "报告", "客户", "deadline", "任务"],
            "学习": ["课程", "笔记", "学习", "考试", "论文", "阅读", "知识"],
            "娱乐": ["电影", "音乐", "游戏", "视频", "娱乐", "休闲", "旅游"],
            "生活": ["购物", "美食", "健康", "家庭", "生活", "日常"]
        }
        
        scores = {cat: 0 for cat in keywords.keys()}
        
        for category, words in keywords.items():
            for word in words:
                if word in text:
                    scores[category] += 1
        
        # 找出最高分
        best_category = max(scores, key=scores.get)
        if scores[best_category] == 0:
            best_category = "其他"
        
        return AIResult(
            success=True,
            content=best_category,
            feature=AIFeature.CLASSIFY,
            metadata={"scores": scores, "method": "keyword_based"}
        )


def create_ai_processor(api_key: Optional[str] = None, 
                        provider: str = "openai",
                        use_local_fallback: bool = True) -> AIProcessor:
    """创建AI处理器工厂函数
    
    Args:
        api_key: API密钥
        provider: 提供商
        use_local_fallback: 如果API不可用，是否使用本地处理
        
    Returns:
        AI处理器实例
    """
    processor = AIProcessor(api_key=api_key, provider=provider)
    
    if not processor.is_available() and use_local_fallback:
        print("Using local AI processor")
        return LocalAIProcessor()
    
    return processor
