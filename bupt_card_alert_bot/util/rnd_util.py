"""
与随机相关的工具函数。
"""

__all__ = ('random_trigger_cmd',)
import secrets

from ..constant import *


def random_trigger_cmd(k: int = DEPLOY_TRIGGER_STR_LEN, alphabet: str = TRIGGER_CMD_ALPHABET,
                       prefix: str = DEFAULT_DEPLOY_COMMAND):
    """
    生成密码学安全的随机部署命令。返回如下字符串：{prefix}{空格}{随机部分}，
    其中随机部分指「由 alphabet 中的字符组成的 k 长字符串」。

    :param k: 随机部分的长度
    :param alphabet: 字母表，控制部署命令的随机字符集
    :param prefix: 前缀（如“/ecard_deploy”，结尾不含空格）
    :return: {prefix}{空格}{由 alphabet 中的字符组成的 k 长字符串}
    """

    random_part = ''.join(secrets.choice(alphabet) for __ in range(k))
    return f'{prefix} {random_part}'
