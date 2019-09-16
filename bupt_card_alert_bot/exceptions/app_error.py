__all__ = ('AppFatalError', 'AppNormalError')


class AppFatalError(RuntimeError):
    """
    标记由当前应用（而非第三方库）抛出的，无法恢复的致命错误。
    """
    pass


class AppNormalError(RuntimeError):
    """
    标记由当前应用（而非第三方库）抛出的，但可以恢复的普通错误。
    """
    pass
