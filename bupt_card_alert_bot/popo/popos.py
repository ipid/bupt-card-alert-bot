__all__ = (
    'EcardUserInfo',
    'SessionKeeper',
    'State',
    'Transaction',
)
from collections import namedtuple

EcardUserInfo = namedtuple('EcardUserInfo', [
    # 学号
    'id',

    # 姓名
    'name',

    # 身份 / 角色（如「本科生」、「研究生」等）
    'role'
])

SessionKeeper = namedtuple('SessionKeeper', [
    # 存放 requests.Session 对象的属性
    'sess'
])

State = namedtuple('State', [
    # 记录当前登录 webvpn 所使用的 cookie
    'cookie',

    # Telegram 机器人是否已部署
    'tg_deployed',

    # 如果 Telegram 机器人已部署，该变量保存使用者的 ID
    'tg_userid',
])

Transaction = namedtuple('Transaction', [
    # 操作时间
    'operation_time',

    # 科目描述
    'category',

    # 交易金额
    'transaction_amount',

    # 余额
    'balance',

    # 终端名称
    'location',
])
