__all__ = ('initialize_logger', 'log_resp')

import datetime
import json
import logging
import sys
from logging import handlers

import requests

from ..constant import *
from ..util import tz_beijing


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

    # 按照日期命名日志，并定期删除老日志，防止日志过大
    trfh = handlers.TimedRotatingFileHandler(
        log_file, when='midnight', backupCount=7, encoding='utf-8',
        # 在每天的北京时间 0 点滚日志
        utc=True, atTime=datetime.time(tzinfo=tz_beijing)
    )
    trfh.setLevel(logging.DEBUG)
    trfh.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(trfh)


def log_resp(logger: logging.Logger, resp: requests.Response) -> None:
    """
    在日志中记录关于 request.get/post() 的返回值 resp 的信息。
    :param logger: 所需的 logger 对象
    :param resp: request.get/post() 的返回值
    :return:
    """
    logger.debug(f'resp = {{\n'
                 f'    url: {resp.url},\n'
                 f'    status_code: {resp.status_code},\n'
                 f'    headers: {resp.headers},\n'
                 f'    text: {json.dumps(resp.text)},\n'
                 f'}}')
