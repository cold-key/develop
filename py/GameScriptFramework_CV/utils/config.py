import json
import os
from typing import Any, Dict, Optional

class Config:
    """配置管理类，用于管理框架的各项配置"""
    
    def __init__(self, config_file: str = "config.json"):
        """
        初始化配置管理器
        
        Args:
            config_file: 配置文件路径
        """
        self.config_file = config_file
        self.config_data = self.load_config()
        
    def load_config(self) -> Dict[str, Any]:
        """
        加载配置文件
        
        Returns:
            配置数据字典
        """
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"加载配置文件失败: {str(e)}")
                return self.get_default_config()
        else:
            return self.get_default_config()
            
    def save_config(self) -> None:
        """保存配置到文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config_data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"保存配置文件失败: {str(e)}")
            
    def get_default_config(self) -> Dict[str, Any]:
        """
        获取默认配置
        
        Returns:
            默认配置字典
        """
        return {
            "image_match": {
                "confidence": 0.8,
                "max_wait_time": 10,
                "check_interval": 0.5
            },
            "input": {
                "click_interval": 0.1,
                "key_interval": 0.1,
                "move_duration": 0.2
            },
            "ocr": {
                "language": "chi_sim+eng",
                "threshold": 127
            },
            "debug": {
                "save_screenshots": False,
                "screenshot_dir": "debug/screenshots"
            }
        }
        
    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置项值
        
        Args:
            key: 配置项键名，支持点号分隔的多级键名
            default: 默认值
            
        Returns:
            配置项值
        """
        try:
            value = self.config_data
            for k in key.split('.'):
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
            
    def set(self, key: str, value: Any) -> None:
        """
        设置配置项值
        
        Args:
            key: 配置项键名，支持点号分隔的多级键名
            value: 配置项值
        """
        keys = key.split('.')
        data = self.config_data
        
        # 遍历到最后一个键之前
        for k in keys[:-1]:
            if k not in data:
                data[k] = {}
            data = data[k]
            
        # 设置最后一个键的值
        data[keys[-1]] = value
        self.save_config()
