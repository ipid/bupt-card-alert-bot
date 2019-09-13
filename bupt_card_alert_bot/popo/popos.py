__all__ = (
    'EcardUserInfo',
    'SessionKeeper',
    'Transaction',
)
from collections import namedtuple

"""
记录 ecard 网站上个人信息。
"""
EcardUserInfo = namedtuple('EcardUserInfo', [
    # 学号
    'id',

    # 姓名
    'name',

    # 身份 / 角色（如「本科生」、「研究生」等）
    'role'
])

"""
用于在各个类之间传递 requests.Session 对象。
"""
SessionKeeper = namedtuple('SessionKeeper', [
    # 存放 requests.Session 对象的属性
    'sess'
])

"""
用于结构化地记录一条消费记录。
"""
Transaction = namedtuple('Transaction', [
    # 操作时间
    'op_datetime',

    # 科目描述
    'category',

    # 交易金额
    'trans_amount',

    # 余额
    'balance',

    # 终端名称
    'location',

    # 操作时间 - Unix 时间戳,
    'op_timestamp',
])
