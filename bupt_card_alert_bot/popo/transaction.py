__all__ = ('Transaction',)
from .base import *


class Transaction:
    """
    该类用于记录从 ecard 官网获取的一条交易（消费记录）的信息。
    """

    __slots__ = (
        # 交易金额
        'transaction_amount',

        # 余额
        'balance',

        # 操作时间
        'operation_time',

        # 科目描述
        'category',

        # 终端名称
        'location',
    )

    def __init__(self, transaction_amount=None, balance=None,
                 operation_time=None, category=None, location=None):
        """
        构造 Transaction 类。所有参数均可留空。
        """
        self.transaction_amount = transaction_amount
        self.balance = balance
        self.operation_time = operation_time
        self.category = category
        self.location = location

    def __repr__(self):
        return base_repr(self)

    def __eq__(self, other):
        return base_eq(self, other)

    def __le__(self, other):
        return base_le(self, other)

    def to_tuple(self) -> tuple:
        """
        将当前的 Transaction 对象用 tuple 表示。
        :return: 用 tuple 表示的当前对象
        """
        return tuple(
            getattr(self, x) for x in Transaction.__slots__
        )

    @staticmethod
    def from_tuple(tp: tuple) -> 'Transaction':
        """
        将用元组表示的 Transaction 类转换为结构化的 Python 类。
        :param tp: 用元组表示的 Transaction 类
        :return: Transaction 类
        """

        if len(tp) != len(Transaction.__slots__):
            raise ValueError('参数 tp 的长度与 Transaction 类属性的个数不匹配。')

        res = Transaction()
        for i, attr in enumerate(Transaction.__slots__):
            setattr(res, attr, tp[i])
        return res
