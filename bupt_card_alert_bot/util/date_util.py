"""
与 Bot 主要逻辑相关的日期、时间函数。
"""

__all__ = ('get_begin_end_date', 'parse_ecard_date',
           'timestamp_now', 'tz_beijing', 'get_reasonable_interval')
import time
import warnings
from datetime import datetime, timedelta, timezone
from typing import Tuple

from ..constant import *

tz_beijing = timezone(timedelta(hours=8))

# 如果查询间隔大于半个小时，就认为是太大了
INTERVAL_TOO_LARGE_THRES = 1800


def is_night(hour: int) -> bool:
    """
    当 0 点到 6 点时，认为是夜晚（不太可能出现消费记录）。
    :param hour: 北京时间的小时数
    :return: bool，是否为夜晚
    """
    return 0 <= hour <= 6


def get_begin_end_date(days: int = DEFAULT_ECARD_TIMEDELTA) -> Tuple[str, str]:
    """
    计算北京时间下的 days 天前的日期和今天日期，作为查询时所使用的开始和结束日期。
    :param days: 天数之差
    :return: (days 天前的日期文本, 今天日期文本)
    """
    today = datetime.now(tz_beijing)
    yesterday = today - timedelta(days=days)

    return yesterday.strftime('%Y-%m-%d'), today.strftime('%Y-%m-%d')


def parse_ecard_date(ecard_date: str) -> int:
    """
    解析 ecard 信息查询网页返回的日期，假设其为北京时间。
    返回 Unix 时间戳。

    :param ecard_date: 形如：2019/9/12 22:52:18 的日期
    :return: Unix 时间戳，int 类型
    """
    dt = datetime.strptime(ecard_date, '%Y/%m/%d %H:%M:%S')
    dt = dt.replace(tzinfo=tz_beijing)
    return int(dt.timestamp())


def timestamp_now() -> int:
    """
    返回当前的 Unix 时间戳（秒，整数）。
    :return: Unix 时间戳（秒，整数）
    """
    return int(time.time())


def get_reasonable_interval(
        day_interval: int = DEFAULT_MAIN_LOOP_INTERVAL['day'],
        night_interval: int = DEFAULT_MAIN_LOOP_INTERVAL['night']) -> int:
    """
    根据当前是白天还是黑夜，返回每一次查询之间的时间间隔。
    :param day_interval: 白天时时间间隔（单位：秒）
    :param night_interval: 晚上时间间隔（单位：秒）
    :return: 时间间隔（单位：秒），int
    """

    # 如果查询间隔大于半个小时，则可能会出现“进入白天，但下一次查询还没开始”的情况
    # 所以当时间过长时，必须警告用户
    if night_interval > INTERVAL_TOO_LARGE_THRES:
        warnings.warn('Your night_interval is too large. '
                      'Less than 1800(half an hour) is recommended.', RuntimeWarning)

    now = datetime.now(tz_beijing)
    if is_night(now.hour):
        return night_interval
    return day_interval
