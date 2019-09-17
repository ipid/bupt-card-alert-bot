__all__ = ('TgBotClient',)

import json
import logging as pym_logging
import math
import time
from typing import Optional, Dict, Any, Tuple

import requests

from ..constant import DEFAULT_TG_POLL_TIMEOUT, RETRY_TIMES
from ..exceptions import AppError
from ..util import retry_post

logger = pym_logging.getLogger(__name__)


class TgBotClient:
    __slots__ = ('token', 'proxies')

    def __init__(self, bot_token: str, proxy_url: Optional[str] = None) -> None:
        self.token = bot_token
        if proxy_url is None:
            self.proxies = None
        else:
            self.proxies = {
                'http': proxy_url,
                'https': proxy_url
            }

    def wait_for_specific_message(self, wait_msg: str,
                                  timeout: int = DEFAULT_TG_POLL_TIMEOUT,
                                  strip_msg: bool = True) -> Optional[int]:
        """
        通过 getUpdates 方法获取新消息，直到获取到某条特定的消息才返回。
        返回该消息的 chat id；如果超时，返回 None。

        :param timeout: 超时时间（单位：秒），超过该时间则返回 None。
        :param wait_msg: 当机器人收到该消息时，方法返回。
        :param strip_msg: 收到消息时是否先将该消息 strip 再判断是否一致。
        :return: 该消息的 chat id，或 None
        """

        # 由于可能获取到非 wait_msg 的消息，所以必须循环获取消息
        if strip_msg:
            wait_msg = wait_msg.strip()

        res = self.__msg_polling_loop(wait_msg, timeout, strip_msg)
        if res is None:
            return None

        chat_id, update_id = res
        self.call('getUpdates', {
            'timeout': 0,
            # 将所收到的消息视作已确认，避免重复收到同一条消息
            'offset': update_id + 1,
        })

        return chat_id

    def __msg_polling_loop(self, wait_msg: str, timeout: int, strip_msg: bool) -> Optional[Tuple[int, int]]:
        """
        通过 Bot API 获取消息的循环。
        :param wait_msg: 见 wait_for_specific_message 方法
        :param timeout: 见 wait_for_specific_message 方法
        :param strip_msg: 见 wait_for_specific_message 方法
        :param
        :return: 元组：对应 wait_msg 的 (chat_id, update_id)
        """

        if not isinstance(timeout, int) or timeout <= 0:
            raise ValueError('timeout 应该为整数类型且大于 0')

        # 记录到超时为止还剩多少时间
        begin_time = time.monotonic()
        # 记录最大的 update_id
        max_update_id = -math.inf
        # 下一次调用 getUpdates 时的 offset 参数
        offset = None

        while True:
            # 计算出该函数已运行了多长时间
            used_time = time.monotonic() - begin_time
            if used_time >= timeout:
                return None

            # 调用 getUpdates，获取到 Update 对象
            updates = self.call('getUpdates', {
                # 将最大超时参数设为剩下的时间
                'timeout': timeout - used_time,
                'offset': offset,
            })

            for update in updates:
                update_id = update.get('update_id', None)
                if update_id is None:
                    logger.debug(f'updates = {updates}')
                    raise AppError('Telegram Bot API 错误：getUpdates 返回的 Update 对象没有 update_id')

                # 记录最大的 update_id
                max_update_id = max(max_update_id, update_id)

                # 获取文本和 chat_id
                msg_txt = update.get('message', {}).get('text', '')
                if strip_msg:
                    msg_txt = msg_txt.strip()

                chat_id = update.get('message', {}).get('chat', {}).get('id', None)

                if msg_txt == wait_msg and chat_id is not None:
                    # 循环出口 #2：如果收到了指定消息，就返回 chat_id 和该 Update 的 update_id
                    return chat_id, update_id

            # 根据 API 文档，offset 参数需比所收到最大的 update_id 大 1
            offset = max_update_id + 1

    def send_message(self, chat_id: int, msg: str, html: bool = True, silent: bool = False) -> None:
        """
        通过该 Telegram Bot，在指定的 chat_id 内发送一条消息。
        方法调用者可以使用简单的 HTML 语法来发送粗体、斜体、等宽字体等格式。
        （parse_mode 为 HTML，具体请参考 Telegram Bot 文档）
        :param chat_id: Chat 的 chat_id
        :param msg: 消息内容
        :param silent: 是否发送无声消息
        :param html: 消息是否解析为 HTML
        :return: None
        """
        param = {
            'chat_id': chat_id,
            'text': msg,
            'disable_notification': silent,
            'disable_web_page_preview': True,
        }

        if html:
            param['parse_mode'] = 'HTML'

        self.call('sendMessage', param)

    def get_bot_name(self) -> Optional[str]:
        """
        调用 Telegram Bot 的 getMe 方法。用于测试 token 是否正确。
        :return: 当前 bot 的个人信息。
        """
        res = self.call('getMe')
        if res.get('id', None) is None:
            raise AppError('调用 getMe 方法错误，无法获取 Bot 信息。')

        return res.get('username', None)

    def call(self, method: str, param: Optional[Dict[str, Any]] = None) -> Any:
        """
        阻塞式调用 Telegram API。
        当远端 API 返回错误时，抛出 AppError。

        :param method: Telegram API 的名字。
        :param param: Telegram API 的参数。
        :return: API 返回值，使用 Python 的类 JSON 格式
        """
        logger.debug(f'Telegram API call: {method}({param})')

        r = retry_post(
            f'https://api.telegram.org/bot{self.token}/{method}',
            proxies=self.proxies,
            json=param,
        )