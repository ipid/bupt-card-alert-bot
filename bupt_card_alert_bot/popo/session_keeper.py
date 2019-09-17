__all__ = ('SessionKeeper',)
from requests import Session


class SessionKeeper:
    """
    用于在各个类之间传递 requests.Session 对象。
    由于 namedtuple 不可变，又无法使用 Python 3.7 的数据类，故声明了原始的类。
    """
    __slots__ = ('sess',)

    def __init__(self, session: Session):
        if session is None:
            raise ValueError('session 参数的值不能为 None。')

        self.sess = session
