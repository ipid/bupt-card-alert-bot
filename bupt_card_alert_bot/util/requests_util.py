__all__ = ('fix_response_encoding', 'RetrySession', 'retry_get', 'retry_post')
import logging as pym_logging
from typing import Any

import chardet
import requests

from ..constant import RETRY_TIMES
from ..exceptions import AppError

DUMMY_OBJ = object()
logger = pym_logging.getLogger(__name__)


def fix_response_encoding(resp: requests.Response) -> None:
    """
    requests 库的 get/post 结果（response）编码时常错乱。
    该函数可通过 chardet 检测编码，来修正 response 的编码。
    该函数对传入的 resp 对象进行原地操作。

    :param resp: requests.get()、post() 的返回值
    :return: None
    """
    res = chardet.detect(resp.content)
    resp.encoding = res['encoding']


def retry_http(req_obj: Any, method: str, url: str,
               retry_times: int, **kwargs) -> requests.Response:
    # 使用唯一的 object 作为判断值是否改变的标准
    err, res = None, DUMMY_OBJ

    # 尝试重复运行 requests API
    for retry_count in range(retry_times):
        try:
            # 如果成功运行，就退出循环，否则继续循环
            res = req_obj.request(method, url, **kwargs)
            break
        except KeyboardInterrupt:
            logger.debug('KeyboardInterrupt during retry_http')
            exit(0)
        except Exception as e:
            # 记住最后一个 err 对象
            err = e

    # 如果未成功执行，就将记录的最后一个 err 抛出去
    if res is DUMMY_OBJ:
        raise AppError(f'向 {url} 发送 {method} 请求已尝试 {retry_times} 次且均未成功。') from err
    return res


def retry_get(url: str, retry_times=RETRY_TIMES, **kwargs) -> requests.Response:
    """
    有重试地调用 requests 的 get 方法。
    当出错时，抛出 IOError。

    :param url: URL
    :param retry_times: 最大重试次数
    :param kwargs: 其它参数（参考 requests 文档）
    :return: requests.Response
    """
    return retry_http(requests, 'get', url, retry_times, **kwargs)


def retry_post(url: str, retry_times=RETRY_TIMES, **kwargs) -> requests.Response:
    """
    有重试地调用 requests 的 post 方法。
    当出错时，抛出 IOError。

    :param url: URL
    :param retry_times: 最大重试次数
    :param kwargs: 其它参数（参考 requests 文档）
    :return: requests.Response
    """
    return retry_http(requests, 'post', url, retry_times, **kwargs)


class RetrySession:
    """
    requests.Session 的包装类，用于使其 get 和 post 方法支持重试功能。
    """
    __slots__ = ('sess',)

    def __init__(self, sess: requests.Session):
        if sess is None:
            raise ValueError('sess 必须为非 None 的对象')

        self.sess = sess

    def get(self, url: str, retry_times=RETRY_TIMES, **kwargs) -> requests.Response:
        """
        有重试地调用 requests 的 get 方法。
        当出错时，抛出 IOError。

        :param url: URL
        :param retry_times: 最大重试次数
        :param kwargs: 其它参数（参考 requests 文档）
        :return: requests.Response
        """
        return retry_http(self.sess, 'get', url, retry_times=retry_times, **kwargs)

    def post(self, url: str, retry_times=RETRY_TIMES, **kwargs) -> requests.Response:
        """
        有重试地调用 requests 的 post 方法。
        当出错时，抛出 IOError。

        :param url: URL
        :param retry_times: 最大重试次数
        :param kwargs: 其它参数（参考 requests 文档）
        :return: requests.Response
        """
        return retry_http(self.sess, 'post', url, retry_times=retry_times, **kwargs)
