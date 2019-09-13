__all__ = ('PathStatus', 'get_path_status',)
from pathlib import Path


class PathStatus:
    # 该路径不存在文件
    NOT_EXIST = 0

    # 该路径存在文件且可以读写
    READABLE = 1

    # 该路径存在同名文件夹等，无法读写
    UNREADABLE = 2


def get_path_status(path: str):
    path = Path(path)

    # 根据文件是否存在进行初始化逻辑
    if path.exists():
        # 如果存在但不是文件，就抛出错误
        if not path.is_file():
            return PathStatus.UNREADABLE
        return PathStatus.READABLE
    else:
        return PathStatus.NOT_EXIST
