__all__ = ('get_begin_end_date',)
from datetime import datetime, timedelta
from typing import Tuple

from ..constant import *


def get_begin_end_date(days=DEFAULT_TIMEDELTA_DAYS) -> Tuple[str, str]:
    """
    计算当前时区下的 days 天前的日期和今天日期，作为查询时所使用的开始和结束日期。
    :param days: 天数之差
    :return: (days 天前的日期, 今天日期)
    """

    today = datetime.now()
    yesterday = today - timedelta(days=days)

    return yesterday.strftime('%Y-%m-%d'), today.strftime('%Y-%m-%d')
