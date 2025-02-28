import time
import random
from typing import Tuple, Optional, Union, List, Callable
import pyautogui
from loguru import logger

class InputController:
    """输入控制器，支持随机时间扰动的输入模拟"""
    
    def __init__(self):
        """初始化输入控制器"""
        # 默认时间扰动范围
        self.move_time_range = (0.1, 0.3)
        self.click_time_range = (0.05, 0.15)
        self.key_time_range = (0.05, 0.15)
        
        # 自定义输入前后处理函数
        self.pre_input_hooks: List[Callable] = []
        self.post_input_hooks: List[Callable] = []
        
    def add_pre_input_hook(self, hook: Callable) -> None:
        """添加输入前处理钩子"""
        self.pre_input_hooks.append(hook)
        
    def add_post_input_hook(self, hook: Callable) -> None:
        """添加输入后处理钩子"""
        self.post_input_hooks.append(hook)
        
    def _execute_hooks(self, hooks: List[Callable]) -> None:
        """执行钩子函数"""
        for hook in hooks:
            try:
                hook()
            except Exception as e:
                logger.error(f"执行钩子函数失败: {str(e)}")
                
    def _get_random_delay(self, time_range: Tuple[float, float]) -> float:
        """生成随机延迟时间"""
        return random.uniform(*time_range)
        
    def _human_like_move(self, 
                        start: Tuple[int, int],
                        end: Tuple[int, int],
                        duration: float) -> None:
        """模拟人类般的鼠标移动"""
        # 生成贝塞尔曲线控制点
        control_points = []
        
        # 添加起点
        control_points.append(start)
        
        # 添加随机中间点
        num_points = random.randint(2, 4)
        for _ in range(num_points):
            x = random.uniform(start[0], end[0])
            y = random.uniform(start[1], end[1])
            control_points.append((x, y))
            
        # 添加终点
        control_points.append(end)
        
        # 计算贝塞尔曲线上的点
        steps = int(duration * 60)  # 60fps
        for t in range(steps + 1):
            t_norm = t / steps
            
            # 计算贝塞尔曲线上的点
            x = y = 0
            n = len(control_points) - 1
            for i, point in enumerate(control_points):
                coef = (
                    (1 - t_norm) ** (n - i)
                    * t_norm ** i
                    * (
                        n
                        / (i * (n - i) if 0 < i < n else 1)
                    )
                )
                x += coef * point[0]
                y += coef * point[1]
                
            pyautogui.moveTo(x, y)
            time.sleep(duration / steps)
            
    def move_to(self,
                position: Tuple[int, int],
                human_like: bool = True) -> None:
        """
        移动鼠标到指定位置
        
        Args:
            position: 目标位置(x, y)
            human_like: 是否模拟人类行为
        """
        try:
            self._execute_hooks(self.pre_input_hooks)
            
            current_pos = pyautogui.position()
            duration = self._get_random_delay(self.move_time_range)
            
            if human_like:
                self._human_like_move(current_pos, position, duration)
            else:
                pyautogui.moveTo(position[0], position[1], duration=duration)
                
            self._execute_hooks(self.post_input_hooks)
            
        except Exception as e:
            logger.error(f"鼠标移动失败: {str(e)}")
            
    def click(self,
             position: Optional[Tuple[int, int]] = None,
             button: str = 'left',
             clicks: int = 1,
             human_like: bool = True) -> None:
        """
        模拟鼠标点击
        
        Args:
            position: 点击位置，None表示当前位置
            button: 鼠标按键
            clicks: 点击次数
            human_like: 是否模拟人类行为
        """
        try:
            self._execute_hooks(self.pre_input_hooks)
            
            if position:
                self.move_to(position, human_like)
                
            for _ in range(clicks):
                pyautogui.click(button=button)
                if clicks > 1:
                    time.sleep(self._get_random_delay(self.click_time_range))
                    
            self._execute_hooks(self.post_input_hooks)
            
        except Exception as e:
            logger.error(f"鼠标点击失败: {str(e)}")
            
    def key_press(self,
                 keys: Union[str, List[str]],
                 presses: int = 1,
                 human_like: bool = True) -> None:
        """
        模拟键盘按键
        
        Args:
            keys: 按键或按键列表
            presses: 按键次数
            human_like: 是否模拟人类行为
        """
        try:
            self._execute_hooks(self.pre_input_hooks)
            
            if isinstance(keys, str):
                keys = [keys]
                
            for _ in range(presses):
                # 按下所有键
                for key in keys[:-1]:
                    pyautogui.keyDown(key)
                    
                # 最后一个键
                pyautogui.press(keys[-1])
                
                # 释放所有键
                for key in reversed(keys[:-1]):
                    pyautogui.keyUp(key)
                    
                if human_like and presses > 1:
                    time.sleep(self._get_random_delay(self.key_time_range))
                    
            self._execute_hooks(self.post_input_hooks)
            
        except Exception as e:
            logger.error(f"键盘按键失败: {str(e)}")
            
    def type_string(self,
                   text: str,
                   human_like: bool = True) -> None:
        """
        模拟键盘输入文本
        
        Args:
            text: 要输入的文本
            human_like: 是否模拟人类行为
        """
        try:
            self._execute_hooks(self.pre_input_hooks)
            
            for char in text:
                pyautogui.write(char)
                if human_like:
                    time.sleep(self._get_random_delay(self.key_time_range))
                    
            self._execute_hooks(self.post_input_hooks)
            
        except Exception as e:
            logger.error(f"文本输入失败: {str(e)}")
            
    def set_time_ranges(self,
                       move_range: Optional[Tuple[float, float]] = None,
                       click_range: Optional[Tuple[float, float]] = None,
                       key_range: Optional[Tuple[float, float]] = None) -> None:
        """
        设置时间扰动范围
        
        Args:
            move_range: 鼠标移动时间范围
            click_range: 点击间隔时间范围
            key_range: 按键间隔时间范围
        """
        if move_range:
            self.move_time_range = move_range
        if click_range:
            self.click_time_range = click_range
        if key_range:
            self.key_time_range = key_range
