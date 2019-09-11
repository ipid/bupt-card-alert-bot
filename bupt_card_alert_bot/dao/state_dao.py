"""
    提供 StateDao 类。
"""

import json

from ..constant import *
from ..popo import State


class StateDao:
    """
        该类提供方便的储存、读取 State 类的接口，以方便本应用崩溃或升级时取回必要的状态信息。
        详细介绍请参考 State 类。
    """

    __slots__ = ('__path',)

    def __init__(self, file_path=DEFAULT_STATE_FILE_PATH):
        self.__path = file_path

    def load_state(self) -> State:
        """
        从数据库获取新的 State 对象。
        :return: State 对象
        """
        with open(self.__path, 'r', encoding=UNIFIED_ENCODING) as f:
            content = json.load(f)
        return State.from_json(content)

    def store_state(self, state: State) -> None:
        """
        将 state 对象持久化储存到数据库中。
        :param state: State 对象
        :return: None
        """
        with open(self.__path, 'w', encoding=UNIFIED_ENCODING) as f:
            json.dump(state.to_json(), f)
