"""
提供 TransactionDao 类。
"""

import json
from typing import Iterable, Set

from ..constant import *
from ..popo import Transaction


class TransactionDao:
    __slots__ = ('__path',)

    def __init__(self, file_path=DEFAULT_TRANSACTION_FILE_PATH):
        self.__path = file_path

    def load_transaction_set(self) -> Set[Transaction]:
        with open(self.__path, 'r', encoding=UNIFIED_ENCODING) as f:
            content = json.load(f)

        return set(Transaction._make(x) for x in content)

    def store_transactions(self, trans: Iterable[Transaction]) -> None:
        trans_list = list(trans)

        with open(self.__path, 'w', encoding=UNIFIED_ENCODING) as f:
            json.dump(trans_list, f)
