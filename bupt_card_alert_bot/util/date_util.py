__all__ = ('default_begin_end_date',)
from datetime import datetime, timedelta
from typing import Tuple


def default_begin_end_date() -> Tuple[str, str]:
    """
    计算当前时区下的昨天日期和今天日期，作为查询时所使用的开始和结束日期。
    :return: (昨天日期, 今天日期)
    """
    today = datetime.now()
    yesterday = today - timedelta(days=1)

    return yesterday.strftime('%Y-%m-%d'), today.strftime('%Y-%m-%d')
