import sys
import os
import time
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.image_processor import ImageMatcher
from core.input_simulator import InputSimulator
from utils.logger import setup_logger
from utils.config import Config

class SimpleGameBot:
    """简单游戏机器人示例"""
    
    def __init__(self):
        # 初始化日志
        self.logger = setup_logger()
        
        # 加载配置
        self.config = Config()
        
        # 创建图像匹配器
        confidence = self.config.get("image_match.confidence", 0.8)
        self.matcher = ImageMatcher(confidence=confidence)
        
        # 设置输入模拟器的默认间隔时间
        click_interval = self.config.get("input.click_interval", 0.1)
        InputSimulator.set_pause(click_interval)
        
    def find_and_click(self, template_path: str, retries: int = 3) -> bool:
        """
        查找并点击目标
        
        Args:
            template_path: 目标图片路径
            retries: 重试次数
            
        Returns:
            是否成功点击目标
        """
        for i in range(retries):
            self.logger.info(f"尝试查找并点击目标: {template_path} (第{i+1}次)")
            
            # 查找目标
            target = self.matcher.find_template(template_path)
            
            if target:
                # 找到目标，执行点击
                position = target[0]  # 获取第一个匹配位置
                InputSimulator.click(position)
                self.logger.info(f"成功点击目标: {position}")
                return True
            else:
                # 未找到目标，等待后重试
                self.logger.warning(f"未找到目标，等待后重试...")
                time.sleep(1)
                
        self.logger.error(f"在{retries}次尝试后仍未找到目标")
        return False
        
    def find_text_and_click(self, text: str, retries: int = 3) -> bool:
        """
        查找并点击文字
        
        Args:
            text: 目标文字
            retries: 重试次数
            
        Returns:
            是否成功点击文字
        """
        for i in range(retries):
            self.logger.info(f"尝试查找并点击文字: {text} (第{i+1}次)")
            
            # 查找文字
            boxes = self.matcher.find_text(text)
            
            if boxes:
                # 找到文字，点击第一个匹配的区域中心
                x, y, w, h = boxes[0]
                center_x = x + w // 2
                center_y = y + h // 2
                InputSimulator.click((center_x, center_y))
                self.logger.info(f"成功点击文字区域: ({center_x}, {center_y})")
                return True
            else:
                # 未找到文字，等待后重试
                self.logger.warning(f"未找到文字，等待后重试...")
                time.sleep(1)
                
        self.logger.error(f"在{retries}次尝试后仍未找到文字")
        return False

def main():
    # 创建机器人实例
    bot = SimpleGameBot()
    
    # 示例：查找并点击开始按钮
    bot.find_and_click("templates/start_button.png")
    
    # 示例：查找并点击包含"开始游戏"文字的按钮
    bot.find_text_and_click("开始游戏")
    
if __name__ == "__main__":
    main()
