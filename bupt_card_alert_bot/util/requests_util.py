__all__ = ('fix_response_encoding',)
import chardet


def fix_response_encoding(resp) -> None:
    """
    requests 库的 get/post 结果（response）编码时常错乱。
    该函数可通过 chardet 检测编码，来修正 response 的编码。
    该函数对传入的 resp 对象进行原地操作。

    :param resp: requests.get()、post() 的返回值
    :return: None
    """
    res = chardet.detect(resp.content)
    resp.encoding = res['encoding']
