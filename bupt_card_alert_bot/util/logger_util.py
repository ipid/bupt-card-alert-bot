__all__ = ('initialize_logger',)

import logging
import sys

from ..constant import *


def initialize_logger(logger: logging.Logger, log_file: str = DEFAULT_LOG_PATH) -> None:
    """
    初始化传入的 Logger 对象，
    将 INFO 以上的日志输出到屏幕，将所有日志存入文件。
    :param logger: 要初始化的 logging.Logger 对象
    :param log_file: 日志文件路径
    :return: None
    """
    logger.setLevel(logging.DEBUG)

    sh = logging.StreamHandler(sys.stdout)
    sh.setLevel(logging.INFO)
    sh.setFormatter(logging.Formatter('[%(levelname)s] %(message)s'))
    logger.addHandler(sh)

    fh = logging.FileHandler(log_file, encoding=UNIFIED_ENCODING)
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(fh)
