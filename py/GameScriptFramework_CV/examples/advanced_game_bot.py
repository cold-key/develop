import sys
import os
import time
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.game_analyzer import GameAnalyzer
from core.input_controller import InputController
from utils.logger import setup_logger
from utils.config import Config

class AdvancedGameBot:
    """高级游戏机器人示例"""
    
    def __init__(self):
        self.logger = setup_logger()
        self.config = Config()
        self.analyzer = GameAnalyzer()
        self.controller = InputController()
        
        # 添加输入前后处理钩子
        self.controller.add_pre_input_hook(self._pre_input)
        self.controller.add_post_input_hook(self._post_input)
        
        # 设置随机时间范围
        self.controller.set_time_ranges(
            move_range=(0.2, 0.4),
            click_range=(0.1, 0.2),
            key_range=(0.05, 0.15)
        )
        
    def _pre_input(self):
        """输入前处理"""
        time.sleep(0.05)  # 短暂延迟
        
    def _post_input(self):
        """输入后处理"""
        time.sleep(0.05)  # 短暂延迟
        
    def extract_game_info(self) -> dict:
        """
        提取游戏信息
        
        Returns:
            游戏信息字典
        """
        game_info = {}
        
        # 提取文字信息
        texts = self.analyzer.extract_text()
        game_info['texts'] = [
            item for item in texts
            if item['confidence'] > 60  # 过滤低置信度的结果
        ]
        
        # 检测运动物体
        motion_objects = self.analyzer.detect_motion(min_area=1000)
        game_info['motion_objects'] = motion_objects
        
        # 分析颜色分布
        color_info = self.analyzer.analyze_color_distribution()
        game_info['colors'] = color_info
        
        return game_info
        
    def find_and_click_text(self, target_text: str) -> bool:
        """
        查找并点击指定文字
        
        Args:
            target_text: 目标文字
            
        Returns:
            是否成功点击
        """
        texts = self.analyzer.extract_text()
        
        for text_info in texts:
            if target_text in text_info['text']:
                # 计算文字框中心位置
                x, y, w, h = text_info['box']
                center = (x + w//2, y + h//2)
                
                # 模拟人类点击
                self.controller.click(center, human_like=True)
                return True
                
        return False
        
    def monitor_game_objects(self, template_path: str) -> list:
        """
        监控游戏对象
        
        Args:
            template_path: 目标模板图片路径
            
        Returns:
            检测到的对象列表
        """
        objects = self.analyzer.detect_objects(template_path)
        return [obj for obj in objects if obj['confidence'] > 0.8]
        
    def perform_action_sequence(self, actions: list) -> None:
        """
        执行动作序列
        
        Args:
            actions: 动作列表，每个动作是一个字典，包含：
                    - type: 动作类型（'click', 'key', 'move'）
                    - params: 动作参数
        """
        for action in actions:
            action_type = action['type']
            params = action['params']
            
            if action_type == 'click':
                self.controller.click(**params)
            elif action_type == 'key':
                self.controller.key_press(**params)
            elif action_type == 'move':
                self.controller.move_to(**params)
                
            # 动作之间添加随机延迟
            time.sleep(random.uniform(0.5, 1.0))

def main():
    # 创建机器人实例
    bot = AdvancedGameBot()
    
    # 示例1：提取游戏信息
    game_info = bot.extract_game_info()
    print("游戏信息:", game_info)
    
    # 示例2：查找并点击文字
    bot.find_and_click_text("开始游戏")
    
    # 示例3：监控游戏对象
    objects = bot.monitor_game_objects("templates/character.png")
    print("检测到的对象:", objects)
    
    # 示例4：执行动作序列
    actions = [
        {
            'type': 'key',
            'params': {'keys': ['w'], 'presses': 1}
        },
        {
            'type': 'click',
            'params': {'position': (500, 300)}
        },
        {
            'type': 'key',
            'params': {'keys': ['ctrl', 'c']}
        }
    ]
    bot.perform_action_sequence(actions)
    
if __name__ == "__main__":
    main()
