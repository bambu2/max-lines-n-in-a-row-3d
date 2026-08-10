import logging
import sys
from logging.handlers import RotatingFileHandler


def get_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # 避免重复添加 Handler（防止日志打印两次）
    if not logger.handlers:
        # 1. 控制台输出
        console = logging.StreamHandler(sys.stdout)
        console.setLevel(logging.INFO)

        # 2. 文件输出（自动切割，单个文件最大 10MB，保留 5 个备份）
        file_handler = RotatingFileHandler(
            "app.log", maxBytes=10 * 1024 * 1024, backupCount=5
        )
        file_handler.setLevel(logging.WARNING)  # 文件只存警告及以上级别

        # 统一格式
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
        )
        console.setFormatter(formatter)
        file_handler.setFormatter(formatter)

        logger.addHandler(console)
        logger.addHandler(file_handler)

    return logger
