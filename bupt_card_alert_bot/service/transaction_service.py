__all__ = ('combine_continuous_small_transactions',)
from itertools import islice
from typing import List

from ..constant import COMBINE_AMOUNT
from ..popo import Transaction


def is_combinable(a: Transaction, b: Transaction, threshold: float) -> bool:
    """
    判断两个传入的 Transaction 对象是否符合
    combine_continuous_small_transactions 文档中的合并条件。
    :param a: Transaction 对象
    :param b: Transaction 对象
    :return: bool，表示是否能合并
    """
    if a.trans_amount >= threshold or b.trans_amount >= threshold:
        return False
    if a.category != b.category or a.location != b.location:
        return False
    return True


def combine_2_transactions(a: Transaction, b: Transaction) -> Transaction:
    a_dict = a._asdict()
    a_dict['trans_amount'] += b.trans_amount
    a_dict['balance'] = b.balance

    res = Transaction(**a_dict)
    return res


def combine_continuous_small_transactions(transactions: List[Transaction],
                                          threshold: float = COMBINE_AMOUNT) -> List[Transaction]:
    """
    合并时间戳连续的，每一笔消费金额都小于 threshold，且消费类别、位置相同的多条消费记录。
    合并后的“交易时间”为第一笔交易，“消费金额”为多笔交易金额之和，“钱包余额”为最后一笔交易的钱包余额。

    :param transactions: list，元素为 Transaction；传入前必须已按时间戳排序
    :param threshold: 连续的小于该参数的消费记录会被合并
    :return: 新的 Transaction list
    """

    if len(transactions) == 0:
        return []

    res = [transactions[0]]

    # 跳过 list 中第一个元素
    for trans in islice(transactions, 1, None):
        # 如果不可合并，就直接插入
        if is_combinable(res[-1], trans, threshold):
            # namedtuple 是不可变的。
            # 先移除最后一个，再插入合并后的新 Transaction
            last = res.pop()
            res.append(combine_2_transactions(last, trans))
        else:
            res.append(trans)

    return res
