from loguru import logger
import sys
import os

def setup_logger(log_dir: str = "logs"):
    """
    配置日志记录器
    
    Args:
        log_dir: 日志文件存储目录
    """
    # 创建日志目录
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
        
    # 配置日志格式
    log_format = "{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
    
    # 移除默认处理器
    logger.remove()
    
    # 添加控制台处理器
    logger.add(sys.stderr, format=log_format, level="INFO")
    
    # 添加文件处理器
    log_file = os.path.join(log_dir, "game_script_{time}.log")
    logger.add(log_file, 
              format=log_format,
              level="DEBUG",
              rotation="500 MB",    # 日志文件大小超过500MB时轮转
              retention="1 week")   # 保留1周的日志
    
    return logger
