__all__ = ('AppError', 'AppFatalError')


class AppError(RuntimeError):
    """
    标记由当前应用（而非第三方库）抛出的，但可以恢复的普通错误。
    该错误应该由接触第三方接口的 DAO、client 等模块抛出，然后由最上层处理。
    """
    pass


class AppFatalError(RuntimeError):
    """
    标记由当前应用（而非第三方库）抛出的，无法恢复的致命错误。
    """
    pass
