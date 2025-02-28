import time
from typing import Tuple, Optional, Union
import pyautogui
from loguru import logger

class InputSimulator:
    """输入模拟器，用于模拟鼠标和键盘操作"""
    
    @staticmethod
    def move_to(position: Tuple[int, int], duration: float = 0.1) -> None:
        """
        移动鼠标到指定位置
        
        Args:
            position: 目标位置坐标(x, y)
            duration: 移动持续时间，单位秒
        """
        try:
            pyautogui.moveTo(position[0], position[1], duration=duration)
        except Exception as e:
            logger.error(f"鼠标移动失败: {str(e)}")
    
    @staticmethod
    def click(position: Optional[Tuple[int, int]] = None,
             button: str = 'left',
             clicks: int = 1,
             interval: float = 0.1) -> None:
        """
        模拟鼠标点击
        
        Args:
            position: 点击位置，None表示当前位置
            button: 鼠标按键，'left'或'right'
            clicks: 点击次数
            interval: 点击间隔时间
        """
        try:
            if position:
                pyautogui.click(position[0], position[1], 
                              button=button, 
                              clicks=clicks, 
                              interval=interval)
            else:
                pyautogui.click(button=button, 
                              clicks=clicks, 
                              interval=interval)
        except Exception as e:
            logger.error(f"鼠标点击失败: {str(e)}")
    
    @staticmethod
    def drag_to(start: Tuple[int, int],
                end: Tuple[int, int],
                duration: float = 0.5) -> None:
        """
        模拟鼠标拖拽
        
        Args:
            start: 起始位置
            end: 结束位置
            duration: 拖拽持续时间
        """
        try:
            pyautogui.moveTo(start[0], start[1])
            pyautogui.dragTo(end[0], end[1], duration=duration)
        except Exception as e:
            logger.error(f"鼠标拖拽失败: {str(e)}")
    
    @staticmethod
    def press_key(key: Union[str, list],
                  presses: int = 1,
                  interval: float = 0.1) -> None:
        """
        模拟键盘按键
        
        Args:
            key: 按键名称或组合键列表
            presses: 按键次数
            interval: 按键间隔时间
        """
        try:
            if isinstance(key, list):
                # 处理组合键
                with pyautogui.hold(key[:-1]):
                    pyautogui.press(key[-1], presses=presses, interval=interval)
            else:
                pyautogui.press(key, presses=presses, interval=interval)
        except Exception as e:
            logger.error(f"键盘按键失败: {str(e)}")
    
    @staticmethod
    def type_string(text: str, interval: float = 0.1) -> None:
        """
        模拟键盘输入文本
        
        Args:
            text: 要输入的文本
            interval: 字符间隔时间
        """
        try:
            pyautogui.write(text, interval=interval)
        except Exception as e:
            logger.error(f"文本输入失败: {str(e)}")
            
    @staticmethod
    def set_pause(seconds: float) -> None:
        """
        设置操作间隔时间
        
        Args:
            seconds: 间隔时间，单位秒
        """
        pyautogui.PAUSE = seconds
