import logging
import os
from datetime import datetime

from src.ai_service.utils.path_tool import abs_path

__all__ = ["log", "LOG_ROOT"]

LOG_ROOT = abs_path("logs")
os.makedirs(LOG_ROOT, exist_ok=True)
DEFAULT_LOG_FORMAT = logging.Formatter(
    '%(asctime)s %(name)-12s %(levelname)-8s - %(filename)s:%(lineno)d - %(message)s'
)


def get_logger(name: str = "agent", console_level: int = logging.INFO, file_level=logging.DEBUG,
               log_file=None) -> logging.Logger:
    """
    创建并配置一个日志记录器，同时支持控制台和文件输出。

    该函数会创建一个指定名称的logger，并配置两个handler：
    1. 控制台输出handler：输出指定级别的日志到控制台
    2. 文件输出handler：输出指定级别的日志到文件中

    Args:
        name (str, optional): 日志记录器的名称，默认为"agent"。名称用于区分不同模块的日志。
        console_level (int, optional): 控制台输出的日志级别，默认为logging.INFO。
            可选值：logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR, logging.CRITICAL
        file_level (int, optional): 文件输出的日志级别，默认为logging.DEBUG。
            可选值：logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR, logging.CRITICAL
        log_file (str, optional): 日志文件路径。如果为None，则使用默认路径
            logs/{name}_{YYYYMMDD}.log格式。

    Returns:
        logging.Logger: 配置好的日志记录器实例。
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    # 避免重复添加 Handler
    if logger.handlers:
        return logger
    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_level)
    console_handler.setFormatter(DEFAULT_LOG_FORMAT)

    logger.addHandler(console_handler)
    if not log_file:
        log_file = os.path.join(LOG_ROOT, f"{name}_{datetime.now().strftime('%Y%m%d')}.log")
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(file_level)
    file_handler.setFormatter(DEFAULT_LOG_FORMAT)

    logger.addHandler(file_handler)
    return logger


log = get_logger()

if __name__ == '__main__':
    print("日志文件夹路径：" + LOG_ROOT)
    log.info("信息日志")
    log.error("错误日志")
    log.warning("警告日志")
    log.debug("调试日志")
