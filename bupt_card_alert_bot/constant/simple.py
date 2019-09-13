"""
此处存放较简单的，单行的常量。
"""

"""
默认的配置文件的路径。
"""
DEFAULT_CONFIG_FILE_PATH = 'config.json'

"""
默认的状态（State）文件的路径。
State 使用 JSON 格式来保存。
"""
DEFAULT_STATE_FILE_PATH = '__state.json'

"""
默认的交易（Transaction）文件的路径。
Transaction 使用 JSON 格式来保存。
"""
DEFAULT_TRANSACTION_FILE_PATH = '__transactions.json'

"""
begin_end_date 函数的默认参数：天数之差
"""
DEFAULT_TIMEDELTA_DAYS = 1

"""
虽然本程序缓存消费记录以防止重复通知，但为了减少内存消耗，需要定期清理旧的消费记录。
该配置指定了默认应该清理掉多久之前的消费记录。

注：修改该值时需确定该值大于查询消费记录的时间跨度。
"""
DELETE_OLD_TRANSACTIONS_DAYS_BEFORE = 2

"""
数据库 URL。默认使用 SQLite。
"""
DATABASE_URL = 'sqlite:///:memory:'

"""
整个应用中所使用的统一的文本编码，用于文件读写、bytes 传输等。
"""
UNIFIED_ENCODING = 'utf-8'

"""
Telegram 客户端中，「等待某条消息」的默认超时时间（秒）。
"""
DEFAULT_TG_POLL_TIMEOUT = 300
