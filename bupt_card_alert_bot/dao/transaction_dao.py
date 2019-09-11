"""
提供 TransactionDao 类。
"""

import json
from typing import Set

from ..constant import *
from ..popo import Transaction


class TransactionDao:
    __slots__ = ('__path',)

    def __init__(self, file_path=DEFAULT_TRANSACTION_FILE_PATH):
        self.__path = file_path

    def load_transaction_set(self) -> Set[Transaction]:
        with open(self.__path, 'r', encoding=UNIFIED_ENCODING) as f:
            content = json.load(f)

        return set(content)

    def store_transaction_set(self, trans: Set[Transaction]) -> None:
        trans_list = list(trans)

        with open(self.__path, 'r', encoding=UNIFIED_ENCODING) as f:
            json.dump(trans_list, f)
