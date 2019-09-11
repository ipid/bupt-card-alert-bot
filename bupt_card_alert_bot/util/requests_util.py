__all__ = ('fix_response_encoding',)

import chardet


def fix_response_encoding(resp) -> None:
    res = chardet.detect(resp.content)
    resp.encoding = res['encoding']
