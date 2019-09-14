"""
提供 ConfigDao 类和单例的 config_dao 实例。
"""
__all__ = ('ConfigDao',)

import json
from typing import Optional

import jsonschema

from ..constant import *
from ..exceptions import AppError


class ConfigDao:
    """
    ConfigDao 类：
    提供读取静态的配置文件的接口。
    初始化时使用默认配置文件路径，可指定别的路径。

    该类并不自带单例模式，且所有方法均不是静态。
    因此，使用该类时，用户应先初始化该类，并全程使用同一个实例。

    TODO: 给别的类注释其使用方法
    """
    __slots__ = ('__conf',)

    def __init__(self, config_filename: str = DEFAULT_CONFIG_FILE_PATH) -> None:
        """
        构造函数。初始化一个已经读入了配置文件的 ConfigDao 类。
        :param config_filename: 配置文件的路径。默认为 DEFAULT_CONFIG_FILE_PATH。
        """
        try:
            with open(config_filename, 'r', encoding=UNIFIED_ENCODING) as f:
                conf = json.load(f)
        except Exception as e:
            raise AppError('配置文件读取失败。') from e

        try:
            # 验证配置文件格式是否正确
            jsonschema.validate(conf, CONFIG_SCHEMA)
        except jsonschema.ValidationError as e:
            # 如果格式不正确，抛出用户友好的错误信息
            raise AppError('配置文件格式错误。') from e

        self.__conf = conf

    def __getitem__(self, item: str) -> Optional[str]:
        """
        获取某个配置。
        :param item: 配置的名字（str）。
        :return: 配置内容（str）
        """
        if item not in CONFIG_VALID_PROPS:
            raise AppError(f'配置名 {item} 不合法。')

        if item not in self.__conf:
            return None

        return self.__conf[item]
