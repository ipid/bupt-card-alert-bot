"""
提供 TransactionDao 类。
"""

__all__ = ('TransactionDao',)

import json
from typing import Iterable, Set

from ..constant import *
from ..exceptions import AppError
from ..popo import Transaction
from ..util import PathStatus, get_path_status


class TransactionDao:
    """
    负责持久化读写“已经发送过通知的消费记录”（Transaction 对象）。
    TODO: 使用 SQLite 等数据库
    """
    __slots__ = ('__path',)

    def __init__(self, file_path: str = DEFAULT_TRANSACTION_FILE_PATH) -> None:
        self.__path = file_path

        ps = get_path_status(file_path)
        if ps == PathStatus.NOT_EXIST:
            self.reset_all()
        elif ps == PathStatus.UNREADABLE:
            raise AppError(f'{file_path} 不是文件，无法覆盖或读取。')

    def reset_all(self) -> None:
        with open(self.__path, 'w', encoding=UNIFIED_ENCODING) as f:
            json.dump([], f)

    def load_transaction_set(self) -> Set[Transaction]:
        with open(self.__path, 'r', encoding=UNIFIED_ENCODING) as f:
            content = json.load(f)

        return set(Transaction._make(x) for x in content)

    def store_transactions(self, trans: Iterable[Transaction]) -> None:
        trans_list = list(trans)

        with open(self.__path, 'w', encoding=UNIFIED_ENCODING) as f:
            json.dump(trans_list, f)
