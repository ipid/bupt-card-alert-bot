"""
    提供 SessionKeeper 类。
"""
__all__ = ('SessionKeeper',)
from requests import Session


class SessionKeeper:
    """
        该类用于保存 requests 库的 Session 对象，方便其在各个 spider 之间传播。
    """

    __slots__ = (
        'sess',
    )

    def __init__(self, session: Session = None):
        self.sess = session
