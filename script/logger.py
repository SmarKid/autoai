import os
import logging
from datetime import datetime

def setup_logger():
    """初始化日志记录器
    
    Returns:
        logging.Logger: 配置好的日志记录器
    """
    # 确保logs目录存在
    log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    # 创建日志文件名，包含日期
    log_file = os.path.join(log_dir, f'autoai_{datetime.now().strftime("%Y%m%d")}.log')
    
    # 配置日志记录器
    logger = logging.getLogger('autoai')
    logger.setLevel(logging.DEBUG)
    
    # 文件处理器
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # 设置日志格式
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # 添加处理器
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

# 创建全局日志记录器实例
logger = setup_logger()