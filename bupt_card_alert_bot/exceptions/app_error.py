__all__ = ('AppError',)


class AppError(RuntimeError):
    """
    标记由当前应用（而非第三方库）抛出的错误。
    """
    pass
