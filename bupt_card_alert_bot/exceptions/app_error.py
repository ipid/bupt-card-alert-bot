"""
定义：给整个应用使用的异常类
"""

__all__ = ('AppError', 'AppFatalError')


class AppError(Exception):
    """
    标记由当前应用（而非第三方库）抛出的，但可以恢复的普通错误。
    该错误应该由接触第三方接口的 DAO、client 等模块抛出，然后由最上层处理。
    """
    pass


class AppFatalError(Exception):
    """
    标记由当前应用（而非第三方库）抛出的，无法恢复的致命错误。
    不建议捕捉本异常。
    """
    pass
