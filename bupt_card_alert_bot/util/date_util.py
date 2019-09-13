__all__ = ('get_begin_end_date', 'parse_ecard_date', 'tz_beijing')
from datetime import datetime, timedelta, timezone
from typing import Tuple

from ..constant import *


def tz_beijing() -> timezone:
    return timezone(timedelta(hours=8))


def get_begin_end_date(days: int = DEFAULT_ECARD_TIMEDELTA) -> Tuple[str, str]:
    """
    计算当前时区下的 days 天前的日期和今天日期，作为查询时所使用的开始和结束日期。
    :param days: 天数之差
    :return: (days 天前的日期, 今天日期)
    """

    today = datetime.now()
    yesterday = today - timedelta(days=days)

    return yesterday.strftime('%Y-%m-%d'), today.strftime('%Y-%m-%d')


def parse_ecard_date(ecard_date: str) -> int:
    """
    解析 ecard 信息查询网页返回的日期。
    返回 Unix 时间戳。

    :param ecard_date: 形如：2019/9/12 22:52:18 的日期
    :return: Unix 时间戳，int 类型
    """
    dt = datetime.strptime(ecard_date, '%Y/%m/%d %H:%M:%S')
    dt = dt.replace(tzinfo=tz_beijing())
    return int(dt.timestamp())
