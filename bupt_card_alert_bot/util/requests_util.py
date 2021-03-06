__all__ = ('fix_response_encoding', 'RetrySession', 'retry_get', 'retry_post')
import logging as pym_logging
from typing import Any
from typing import Tuple

import chardet
import requests

from ..constant import *
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


def retry_http(req_obj: Any, method: str, url: str, retry_times: int,
               timeout: Tuple[float, float], **kwargs) -> requests.Response:
    """
    内部函数，外部代码不应使用。将与出错重试相关的代码抽象成了一个函数。
    该函数重复调用 retry_times 次 requests 的 API，如果成功执行则退出循环，否则抛出 AppError，
    将最后一次循环捕捉到的异常作为其 cause 属性。

    :param req_obj: 拥有 request 方法，使用方式类似 requests 的对象（如 Session）
    :param method: HTTP 方法（GET、POST 等）
    :param url: URL
    :param retry_times: 最大重试次数
    :param timeout: 超时时间（使用默认即可，参考 requests 文档）
    :param kwargs: 其它参数（参考 requests 文档）
    :return: requests.Response
    """
    # 声明变量。使用唯一的 object 作为判断值是否改变的标准
    err, res = None, DUMMY_OBJ

    # 尝试重复运行 requests API
    for retry_count in range(retry_times):
        try:
            # 如果成功运行，就退出循环，否则继续循环
            res = req_obj.request(method, url, timeout=timeout, **kwargs)
            break
        except KeyboardInterrupt:
            logger.debug('retry_http 运行时发生了 KeyboardInterrupt')
            exit(0)
        except Exception as e:
            # 记住最后一个 err 对象
            err = e

    # 如果未成功执行，就将记录的最后一个 err 抛出去
    if res is DUMMY_OBJ:
        raise AppError(f'向 {url} 发送 {method} 请求已尝试 {retry_times} 次且均未成功。') from err
    return res


def retry_get(url: str, retry_times=RETRY_TIMES,
              timeout: Tuple[float, float] = DEFAULT_REQ_TIMEOUT, **kwargs) -> requests.Response:
    """
    有重试地调用 requests 的 get 方法。
    当出错时，抛出 IOError。

    :param url: URL
    :param retry_times: 最大重试次数
    :param timeout: 超时时间（使用默认即可，参考 requests 文档）
    :param kwargs: 其它参数（参考 requests 文档）
    :return: requests.Response
    """
    return retry_http(requests, 'get', url, retry_times, timeout, **kwargs)


def retry_post(url: str, retry_times=RETRY_TIMES,
               timeout: Tuple[float, float] = DEFAULT_REQ_TIMEOUT, **kwargs) -> requests.Response:
    """
    有重试地调用 requests 的 post 方法。
    当出错时，抛出 IOError。

    :param url: URL
    :param retry_times: 最大重试次数
    :param timeout: 超时时间（使用默认即可，参考 requests 文档）
    :param kwargs: 其它参数（参考 requests 文档）
    :return: requests.Response
    """
    return retry_http(requests, 'post', url, retry_times, timeout, **kwargs)


class RetrySession:
    """
    requests.Session 的包装类，用于使其 get 和 post 方法支持重试功能。
    """
    __slots__ = ('sess',)

    def __init__(self, sess: requests.Session):
        if sess is None or not isinstance(sess, requests.Session):
            raise ValueError('sess 不能为 None，且必须为 Session 类型的对象')

        self.sess = sess

    def get(self, url: str, retry_times=RETRY_TIMES,
            timeout: Tuple[float, float] = DEFAULT_REQ_TIMEOUT, **kwargs) -> requests.Response:
        """
        有重试地调用 requests 的 get 方法。
        当出错时，抛出 IOError。

        :param url: URL
        :param retry_times: 最大重试次数
        :param timeout: 超时时间（使用默认即可，参考 requests 文档）
        :param kwargs: 其它参数（参考 requests 文档）
        :return: requests.Response
        """
        return retry_http(self.sess, 'get', url, retry_times=retry_times,
                          timeout=timeout, **kwargs)

    def post(self, url: str, retry_times=RETRY_TIMES,
             timeout: Tuple[float, float] = DEFAULT_REQ_TIMEOUT, **kwargs) -> requests.Response:
        """
        有重试地调用 requests 的 post 方法。
        当出错时，抛出 IOError。

        :param url: URL
        :param retry_times: 最大重试次数
        :param timeout: 超时时间（使用默认即可，参考 requests 文档）
        :param kwargs: 其它参数（参考 requests 文档）
        :return: requests.Response
        """
        return retry_http(self.sess, 'post', url, retry_times=retry_times,
                          timeout=timeout, **kwargs)

    def cookies(self) -> Any:
        """
        返回 Session 对象的 cookies 属性。
        :return: Any
        """
        return self.sess.cookies
