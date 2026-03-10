import os
import logging
from logging.handlers import RotatingFileHandler
from constants import ENABLE_LOGGING, LOG_LEVEL, LOG_FILE

def setup_logger():
    """设置并返回日志记录器"""
    logger = logging.getLogger('file_classifier')
    
    # 避免重复添加处理器
    if logger.handlers:
        return logger
        
    # 设置日志级别
    log_level = getattr(logging, LOG_LEVEL.upper(), logging.INFO)
    logger.setLevel(log_level)
    
    if ENABLE_LOGGING:
        # 获取应用程序所在目录
        app_dir = os.path.dirname(os.path.abspath(__file__))
        
        # 创建log目录
        log_dir = os.path.join(app_dir, 'log')
        os.makedirs(log_dir, exist_ok=True)
        
        # 日志文件完整路径
        log_file_path = os.path.join(log_dir, LOG_FILE)
        
        # 创建文件处理器（使用 RotatingFileHandler 限制日志文件大小）
        file_handler = RotatingFileHandler(
            log_file_path, 
            maxBytes=5*1024*1024,  # 5MB
            backupCount=3,
            encoding='utf-8'
        )
        
        # 创建控制台处理器
        console_handler = logging.StreamHandler()
        
        # 设置日志格式
        formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # 添加处理器到日志记录器
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        logger.info("日志系统初始化完成")
    
    return logger

# 创建全局日志实例
logger = setup_logger()
