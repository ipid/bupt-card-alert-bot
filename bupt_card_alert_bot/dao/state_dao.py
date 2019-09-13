"""
提供 StateDao 单例对象。
"""
__all__ = ('StateDao',)

import json
from copy import deepcopy
from typing import Any

from ..constant import *
from ..exceptions import AppError
from ..util import get_path_status, PathStatus

STATES_AND_DEFAULTS = {
    # Telegram 机器人是否已部署
    'tg_deployed': False,

    # 如果 Telegram 机器人已部署，该变量保存使用者的 ID
    'tg_chat_id': None,
}


class StateDao:
    """
    StateDao 负责持久化存取程序的状态信息。
    修改本类的属性时，修改的内容将会自动持久化。
    """
    __slots__ = ('__path', '__conf')

    def __init__(self, path=DEFAULT_STATE_FILE_PATH):
        self.__path = path

        ps = get_path_status(path)
        if ps == PathStatus.NOT_EXIST:
            self.reset_all()
        elif ps == PathStatus.READABLE:
            with path.open('r', encoding=UNIFIED_ENCODING) as f:
                self.__conf = json.load(f)
        else:
            raise AppError(f'{path} 不是文件，无法覆盖或读取。')

    def reset_all(self) -> None:
        """
        生成新状态文件，并将内存中的状态初始化。
        （使用前必须初始化 __path）
        :return: None
        """
        self.__conf = deepcopy(STATES_AND_DEFAULTS)
        self.__persist()

    def __persist(self):
        """
        将 self.__conf 持久化保存。
        :return: None
        """
        with open(self.__path, 'w', encoding=UNIFIED_ENCODING) as f:
            json.dump(self.__conf, f)

    def __getitem__(self, item: str) -> str:
        """
        获取状态（State）中的某一条。
        :param item: 条目的名字（str）。
        :return: 内容（str）
        """
        if item not in STATES_AND_DEFAULTS:
            raise AppError(f'要访问的状态条目 {item} 不存在。')
        return self.__conf[item]

    def __setitem__(self, key: str, value: Any) -> None:
        """
        设置状态中的某一条。
        :param key: 条目的名字（str）。
        :param value: 内容（str）
        :return: None
        """
        if key not in STATES_AND_DEFAULTS:
            raise AppError(f'要设置的状态条目 {key} 不存在。')

        self.__conf[key] = value
        self.__persist()
