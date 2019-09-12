"""
提供 StateDao 类。
"""
__all__ = ('state_dao',)

import json

from ..constant import *
from ..popo import State


class StateDao(State):
    """
    修改本类的属性时，修改的内容将会自动持久化。
    """

    __slots__ = ('__path',)

    def __init__(self):
        self.__path = DEFAULT_STATE_FILE_PATH

    def set_file_path(self, path: str) -> None:
        self.__path = path

    def get_file_path(self) -> str:
        return self.__path

    def __setitem__(self, key: str, value: str) -> None:


    def __getitem__(self, item: str) -> str:
        """
        获取某个配置。
        :param item: 配置的名字（key）。
        :return: 配置内容（str）
        """
        return self.__conf[item]


state_dao = StateDao()
