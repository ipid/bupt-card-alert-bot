__all__ = ('State',)
from typing import Dict, Any
from .base import base_from_json, base_to_json


class State:
    """
    该类用于记录本应用的状态。
    当本应用崩溃或升级重启时，就可以从 State 中恢复所需要的信息。
    所需要的信息举例：vpn 的 cookie、当前 Telegram bot 是否已部署。
    """

    __slots__ = (
        # 记录当前登录 webvpn 所使用的 cookie
        'cookie',

        # Telegram 机器人是否已部署
        'tg_deployed',

        # 如果 Telegram 机器人已部署，该变量保存使用者的 ID
        'tg_userid',
    )

    def __init__(self, cookie=None, tg_deployed=None, tg_userid=None) -> None:
        """
        初始化 State 类。
        """
        self.cookie = cookie
        self.tg_deployed = tg_deployed
        self.tg_userid = tg_userid

    def to_json(self) -> Dict[str, Any]:
        """
        将当前类序列化为适合用 JSON 保存的格式。
        :return: dict 表示的 State 类。
        """
        return base_to_json(self)

    @staticmethod
    def from_json(obj: Dict[str, Any]) -> 'State':
        """
        从使用 JSON 格式表示的 State 对象中解析出 State 对象。
        该方法为静态方法，返回全新的 State 对象。
        该方法假设传入的 JSON 对象是通过 State.to_json 来产生的，请不要使用它来解析任意来源的 State 对象。

        :param obj: 使用 JSON 格式表示的 State 对象
        :return: 新的 State 对象
        """
        return base_from_json(State, obj)
