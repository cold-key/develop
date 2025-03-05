import cv2
import numpy as np
import pytesseract
from typing import List, Tuple, Dict, Optional, Any
import pyautogui
from loguru import logger
import time

class GameAnalyzer:
    """游戏画面分析器，用于提取游戏中的各种信息"""
    
    def __init__(self):
        """初始化游戏分析器"""
        self._last_frame = None
        self._last_frame_time = 0
        self.frame_cache_time = 0.03  # 帧缓存时间（秒）
        
    def get_frame(self, region: Optional[Tuple[int, int, int, int]] = None) -> np.ndarray:
        """
        获取游戏画面帧
        
        Args:
            region: 截图区域(x, y, width, height)
            
        Returns:
            numpy数组格式的画面帧
        """
        current_time = time.time()
        
        # 如果缓存的帧足够新，直接返回
        if (self._last_frame is not None and 
            current_time - self._last_frame_time < self.frame_cache_time):
            return self._last_frame
            
        # 捕获新帧
        screenshot = pyautogui.screenshot(region=region)
        frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        
        self._last_frame = frame
        self._last_frame_time = current_time
        return frame
        
    def extract_text(self, 
                    region: Optional[Tuple[int, int, int, int]] = None,
                    lang: str = 'chi_sim+eng',
                    preprocessing: str = 'default') -> List[Dict[str, Any]]:
        """
        提取画面中的文字
        
        Args:
            region: 识别区域
            lang: OCR语言
            preprocessing: 预处理方法('default', 'threshold', 'adaptive')
            
        Returns:
            文字信息列表，每项包含：
            - text: 识别出的文字
            - confidence: 置信度
            - box: 文字框位置(x, y, w, h)
        """
        frame = self.get_frame(region)
        
        # 图像预处理
        if preprocessing == 'threshold':
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            processed = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        elif preprocessing == 'adaptive':
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            processed = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                           cv2.THRESH_BINARY, 11, 2)
        else:
            processed = frame
            
        # OCR识别
        data = pytesseract.image_to_data(processed, lang=lang, 
                                       output_type=pytesseract.Output.DICT)
        
        results = []
        for i, text in enumerate(data['text']):
            if text.strip():  # 忽略空文本
                results.append({
                    'text': text,
                    'confidence': float(data['conf'][i]),
                    'box': (data['left'][i], data['top'][i],
                           data['width'][i], data['height'][i])
                })
                
        return results
        
    def detect_objects(self, 
                      template_path: str,
                      threshold: float = 0.8,
                      region: Optional[Tuple[int, int, int, int]] = None) -> List[Dict[str, Any]]:
        """
        检测画面中的特定对象
        
        Args:
            template_path: 模板图片路径
            threshold: 匹配阈值
            region: 检测区域
            
        Returns:
            对象信息列表，每项包含：
            - position: 中心位置(x, y)
            - confidence: 匹配置信度
            - box: 边界框(x, y, w, h)
        """
        frame = self.get_frame(region)
        template = cv2.imread(template_path)
        
        result = cv2.matchTemplate(frame, template, cv2.TM_CCOEFF_NORMED)
        h, w = template.shape[:2]
        
        # 找出所有匹配位置
        locations = np.where(result >= threshold)
        objects = []
        
        for pt in zip(*locations[::-1]):
            objects.append({
                'position': (pt[0] + w//2, pt[1] + h//2),
                'confidence': float(result[pt[1], pt[0]]),
                'box': (pt[0], pt[1], w, h)
            })
            
        return objects
        
    def detect_motion(self, 
                     region: Optional[Tuple[int, int, int, int]] = None,
                     min_area: int = 500) -> List[Dict[str, Any]]:
        """
        检测画面中的运动物体
        
        Args:
            region: 检测区域
            min_area: 最小运动区域面积
            
        Returns:
            运动物体信息列表，每项包含：
            - center: 中心位置(x, y)
            - box: 边界框(x, y, w, h)
            - area: 面积
        """
        current_frame = self.get_frame(region)
        if self._last_frame is None:
            self._last_frame = current_frame
            return []
            
        # 计算帧差
        frame_diff = cv2.absdiff(self._last_frame, current_frame)
        gray_diff = cv2.cvtColor(frame_diff, cv2.COLOR_BGR2GRAY)
        
        # 阈值处理
        _, thresh = cv2.threshold(gray_diff, 25, 255, cv2.THRESH_BINARY)
        
        # 查找轮廓
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, 
                                     cv2.CHAIN_APPROX_SIMPLE)
                                     
        motion_objects = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if area >= min_area:
                x, y, w, h = cv2.boundingRect(contour)
                center = (x + w//2, y + h//2)
                motion_objects.append({
                    'center': center,
                    'box': (x, y, w, h),
                    'area': area
                })
                
        return motion_objects
        
    def analyze_color_distribution(self, 
                                 region: Optional[Tuple[int, int, int, int]] = None,
                                 target_color: Optional[Tuple[int, int, int]] = None,
                                 tolerance: int = 20) -> Dict[str, Any]:
        """
        分析画面颜色分布
        
        Args:
            region: 分析区域
            target_color: 目标颜色(B,G,R)
            tolerance: 颜色容差
            
        Returns:
            颜色分析结果，包含：
            - dominant_colors: 主要颜色列表
            - color_ratio: 目标颜色占比（如果指定了目标颜色）
        """
        frame = self.get_frame(region)
        
        # 将图像转换为一维数组
        pixels = frame.reshape(-1, 3)
        
        # 计算主要颜色
        from sklearn.cluster import KMeans
        kmeans = KMeans(n_clusters=5, random_state=42)
        kmeans.fit(pixels)
        colors = kmeans.cluster_centers_
        
        result = {
            'dominant_colors': colors.tolist()
        }
        
        # 如果指定了目标颜色，计算其占比
        if target_color:
            mask = np.all(np.abs(pixels - target_color) <= tolerance, axis=1)
            ratio = np.sum(mask) / len(pixels)
            result['color_ratio'] = float(ratio)
            
        return result
