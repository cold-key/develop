import cv2
import numpy as np
from typing import Tuple, Optional, List
from loguru import logger

class ImageMatcher:
    """图像匹配器，用于在游戏画面中定位目标元素"""
    
    def __init__(self, confidence: float = 0.8):
        """
        初始化图像匹配器
        
        Args:
            confidence: 匹配置信度阈值，范围0-1，越大越严格
        """
        self.confidence = confidence
        self.screen_cache = None
        self.template_cache = {}
        
    def capture_screen(self, region: Optional[Tuple[int, int, int, int]] = None) -> np.ndarray:
        """
        捕获屏幕截图
        
        Args:
            region: 截图区域，格式为(x, y, width, height)，None表示全屏
            
        Returns:
            numpy数组格式的截图
        """
        import pyautogui
        screenshot = pyautogui.screenshot(region=region)
        return cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    
    def load_template(self, template_path: str) -> np.ndarray:
        """
        加载模板图片
        
        Args:
            template_path: 模板图片路径
            
        Returns:
            numpy数组格式的模板图片
        """
        if template_path not in self.template_cache:
            template = cv2.imread(template_path)
            if template is None:
                raise FileNotFoundError(f"无法加载模板图片: {template_path}")
            self.template_cache[template_path] = template
        return self.template_cache[template_path]
    
    def find_template(self, template_path: str, 
                     region: Optional[Tuple[int, int, int, int]] = None,
                     multi_target: bool = False) -> Optional[List[Tuple[int, int]]]:
        """
        在屏幕中查找模板图片
        
        Args:
            template_path: 模板图片路径
            region: 搜索区域，None表示全屏
            multi_target: 是否查找多个目标
            
        Returns:
            如果找到目标，返回目标中心点坐标列表；否则返回None
        """
        try:
            screen = self.capture_screen(region)
            template = self.load_template(template_path)
            
            # 执行模板匹配
            result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
            
            if multi_target:
                # 查找多个目标
                locations = np.where(result >= self.confidence)
                points = []
                for pt in zip(*locations[::-1]):
                    h, w = template.shape[:2]
                    center_x = pt[0] + w // 2
                    center_y = pt[1] + h // 2
                    points.append((center_x, center_y))
                return points if points else None
            else:
                # 查找单个目标
                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                if max_val >= self.confidence:
                    h, w = template.shape[:2]
                    center_x = max_loc[0] + w // 2
                    center_y = max_loc[1] + h // 2
                    return [(center_x, center_y)]
                return None
                
        except Exception as e:
            logger.error(f"模板匹配失败: {str(e)}")
            return None
            
    def find_text(self, text: str, lang: str = 'chi_sim+eng') -> Optional[List[Tuple[int, int, int, int]]]:
        """
        在屏幕中查找文字
        
        Args:
            text: 要查找的文字
            lang: OCR语言，默认中英文
            
        Returns:
            文字区域坐标列表，格式为(x, y, width, height)
        """
        try:
            import pytesseract
            screen = self.capture_screen()
            
            # 图像预处理
            gray = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)
            thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
            
            # OCR识别
            data = pytesseract.image_to_data(thresh, lang=lang, output_type=pytesseract.Output.DICT)
            
            boxes = []
            for i, word in enumerate(data['text']):
                if text in word:
                    x = data['left'][i]
                    y = data['top'][i]
                    w = data['width'][i]
                    h = data['height'][i]
                    boxes.append((x, y, w, h))
                    
            return boxes if boxes else None
            
        except Exception as e:
            logger.error(f"文字识别失败: {str(e)}")
            return None
