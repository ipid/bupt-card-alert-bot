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
DEFAULT_STATE_FILE_PATH = 'state.json'

"""
默认的交易（Transaction）文件的路径。
Transaction 使用 JSON 格式来保存。
"""
DEFAULT_TRANSACTION_FILE_PATH = 'transactions.json'

"""
数据库 URL。默认使用 SQLite。
"""
DATABASE_URL = 'sqlite:///:memory:'

"""
整个应用中所使用的统一的文本编码，用于文件读写、bytes 传输等。
"""
UNIFIED_ENCODING = 'utf-8'
