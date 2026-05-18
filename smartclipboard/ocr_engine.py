"""
OCR引擎模块 - 提供图像文字识别功能
"""

import os
import io
import base64
from typing import Optional, List, Dict
from dataclasses import dataclass
import logging

# 禁用Paddle的日志
logging.getLogger('paddle').setLevel(logging.WARNING)


@dataclass
class OCRResult:
    """OCR识别结果"""
    text: str
    confidence: float
    bbox: List[List[int]]  # 边界框坐标 [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
    
    def __str__(self):
        return f"OCRResult(text='{self.text[:50]}...', confidence={self.confidence:.2f})"


class OCREngine:
    """OCR引擎 - 支持多种OCR后端"""
    
    def __init__(self, use_gpu: bool = False, lang: str = 'ch'):
        """初始化OCR引擎
        
        Args:
            use_gpu: 是否使用GPU加速
            lang: 识别语言，支持 'ch'(中文), 'en'(英文), 'ch_en'(中英混合)
        """
        self.use_gpu = use_gpu
        self.lang = lang
        self._ocr = None
        self._initialized = False
        self._backend = "none"
        
        # 尝试初始化PaddleOCR
        self._init_paddleocr()
    
    def _init_paddleocr(self):
        """初始化PaddleOCR"""
        try:
            from paddleocr import PaddleOCR
            
            # 根据语言设置
            if self.lang == 'ch':
                lang_code = 'ch'
            elif self.lang == 'en':
                lang_code = 'en'
            else:
                lang_code = 'ch'  # 默认中文
            
            self._ocr = PaddleOCR(
                use_angle_cls=True,
                lang=lang_code,
                use_gpu=self.use_gpu,
                show_log=False
            )
            self._initialized = True
            self._backend = "paddleocr"
            print(f"OCR Engine initialized with PaddleOCR ({lang_code})")
        except Exception as e:
            print(f"PaddleOCR initialization failed: {e}")
            self._initialized = False
    
    def is_available(self) -> bool:
        """检查OCR是否可用"""
        return self._initialized
    
    def recognize_image(self, image_path: str) -> List[OCRResult]:
        """识别图片中的文字
        
        Args:
            image_path: 图片文件路径
            
        Returns:
            OCR结果列表
        """
        if not self._initialized:
            return []
        
        try:
            result = self._ocr.ocr(image_path, cls=True)
            return self._parse_result(result)
        except Exception as e:
            print(f"OCR recognition error: {e}")
            return []
    
    def recognize_bytes(self, image_bytes: bytes) -> List[OCRResult]:
        """识别字节数据中的图片文字
        
        Args:
            image_bytes: 图片字节数据
            
        Returns:
            OCR结果列表
        """
        if not self._initialized:
            return []
        
        try:
            import numpy as np
            from PIL import Image
            
            # 转换为numpy数组
            image = Image.open(io.BytesIO(image_bytes))
            image_array = np.array(image)
            
            result = self._ocr.ocr(image_array, cls=True)
            return self._parse_result(result)
        except Exception as e:
            print(f"OCR recognition error: {e}")
            return []
    
    def recognize_clipboard_image(self) -> List[OCRResult]:
        """识别剪贴板中的图片
        
        Returns:
            OCR结果列表
        """
        try:
            # 尝试从剪贴板获取图片
            import sys
            if sys.platform == 'darwin':
                return self._recognize_macos_clipboard()
            elif sys.platform == 'win32':
                return self._recognize_windows_clipboard()
            else:
                return []
        except Exception as e:
            print(f"Clipboard OCR error: {e}")
            return []
    
    def _recognize_macos_clipboard(self) -> List[OCRResult]:
        """识别macOS剪贴板图片"""
        try:
            from AppKit import NSPasteboard
            
            pb = NSPasteboard.generalPasteboard()
            
            # 尝试获取PNG
            image_data = pb.dataForType_("public.png")
            if not image_data:
                image_data = pb.dataForType_("public.tiff")
            
            if image_data:
                return self.recognize_bytes(bytes(image_data))
            
            return []
        except Exception as e:
            print(f"macOS clipboard OCR error: {e}")
            return []
    
    def _recognize_windows_clipboard(self) -> List[OCRResult]:
        """识别Windows剪贴板图片"""
        try:
            import win32clipboard
            import win32con
            from PIL import Image
            import io
            
            win32clipboard.OpenClipboard()
            
            # 检查是否有图片
            if win32con.CF_DIB in range(1, 100):
                try:
                    dib_data = win32clipboard.GetClipboardData(win32con.CF_DIB)
                    win32clipboard.CloseClipboard()
                    
                    # 转换DIB为图片
                    return self.recognize_bytes(dib_data)
                except:
                    pass
            
            win32clipboard.CloseClipboard()
            return []
        except Exception as e:
            try:
                win32clipboard.CloseClipboard()
            except:
                pass
            print(f"Windows clipboard OCR error: {e}")
            return []
    
    def _parse_result(self, result) -> List[OCRResult]:
        """解析OCR结果"""
        ocr_results = []
        
        if not result or not result[0]:
            return ocr_results
        
        for line in result[0]:
            if line:
                bbox = line[0]  # 边界框
                text_info = line[1]  # (text, confidence)
                
                if text_info:
                    text = text_info[0]
                    confidence = text_info[1]
                    
                    ocr_result = OCRResult(
                        text=text,
                        confidence=confidence,
                        bbox=bbox
                    )
                    ocr_results.append(ocr_result)
        
        return ocr_results
    
    def get_full_text(self, results: List[OCRResult]) -> str:
        """获取完整的识别文本
        
        Args:
            results: OCR结果列表
            
        Returns:
            合并后的文本
        """
        return '\n'.join([r.text for r in results])
    
    def get_text_with_confidence(self, results: List[OCRResult], min_confidence: float = 0.8) -> str:
        """获取高置信度的文本
        
        Args:
            results: OCR结果列表
            min_confidence: 最小置信度阈值
            
        Returns:
            过滤后的文本
        """
        filtered = [r.text for r in results if r.confidence >= min_confidence]
        return '\n'.join(filtered)


class MockOCREngine:
    """模拟OCR引擎 - 用于测试或无OCR依赖的环境"""
    
    def __init__(self):
        self._initialized = True
        self._backend = "mock"
    
    def is_available(self) -> bool:
        return True
    
    def recognize_image(self, image_path: str) -> List[OCRResult]:
        """模拟识别 - 返回示例结果"""
        return [
            OCRResult(
                text="[模拟OCR] 请安装PaddleOCR以启用真实识别功能",
                confidence=1.0,
                bbox=[[0, 0], [100, 0], [100, 30], [0, 30]]
            )
        ]
    
    def recognize_bytes(self, image_bytes: bytes) -> List[OCRResult]:
        return self.recognize_image("")
    
    def recognize_clipboard_image(self) -> List[OCRResult]:
        return self.recognize_image("")
    
    def get_full_text(self, results: List[OCRResult]) -> str:
        return '\n'.join([r.text for r in results])


def create_ocr_engine(use_gpu: bool = False, lang: str = 'ch', fallback_to_mock: bool = True) -> OCREngine:
    """创建OCR引擎工厂函数
    
    Args:
        use_gpu: 是否使用GPU
        lang: 语言
        fallback_to_mock: 如果真实OCR初始化失败，是否使用模拟引擎
        
    Returns:
        OCREngine实例
    """
    engine = OCREngine(use_gpu=use_gpu, lang=lang)
    
    if not engine.is_available() and fallback_to_mock:
        print("Using mock OCR engine")
        return MockOCREngine()
    
    return engine
