"""
本文件提供 VpnClient 类。
该类负责访问北邮 WebVpn 网站。
"""

__all__ = ('VpnClient',)

import logging as pym_logging

from ..exceptions import AppError
from ..popo import SessionKeeper
from ..util import fix_response_encoding
from ..service import log_resp

logger = pym_logging.getLogger(__name__)


class VpnClient:
    """
    该类负责访问北邮 WebVpn 网站，提供模拟登录等功能。
    该类应该通过保存 Session 的方式来实现，使该类的使用方式符合人类直觉。
    """

    __slots__ = ('sess_keep',)

    def __init__(self, session_keeper: SessionKeeper) -> None:
        if session_keeper.sess is None:
            raise ValueError('SessionKeeper 中必须有已初始化的 requests.Session 对象')

        self.sess_keep = session_keeper

    def obtain_sessid(self) -> None:
        """
        访问登录页面，以获取服务器设置的 cookie PHPSESSID。
        :return: None
        """
        logger.debug('调用 obtain_sessid')
        sess = self.sess_keep.sess

        # 获取 PHPSESSID
        # --- 吐槽：这个网站会返回十一个 Set-Cookie 头，重要的 Cookie 要设 11 遍 ---（划掉）
        sess.get('https://vpn.bupt.edu.cn/global-protect/login.esp')
        logger.debug(f'sess.cookies() = {str(sess.cookies())}')

        if sess.cookies() is None:
            raise AppError('无法获取 PHPSESSID')
        if 'PHPSESSID' not in sess.cookies():
            raise AppError('无法获取 PHPSESSID')

    def login(self, username: str, password: str) -> None:
        logger.debug('登录 webvpn')
        sess = self.sess_keep.sess

        resp = sess.post('https://vpn.bupt.edu.cn/global-protect/login.esp', data={
            'prot': 'https:',
            'server': 'vpn.bupt.edu.cn',
            'inputStr': '',
            'action': 'getsoftware',
            'user': username,
            'passwd': password,
            'ok': 'Log In'
        })
        fix_response_encoding(resp)

        # 检测 GP_SESSION_CK 是否在 cookies 中，如果存在说明登录成功
        if 'GP_SESSION_CK' not in sess.cookies():
            logger.debug(f'sess.cookies() = {str(sess.cookies())}, resp.url = {resp.url}')
            raise AppError('登录失败（未获取到 GP_SESSION_CK），可能是用户名或密码错误。')

        if username not in resp.text or '客户端下载' not in resp.text:
            logger.debug(f'sess.cookies() = {str(sess.cookies())}, resp.url = {resp.url}')
            log_resp(logger, resp)
            raise AppError('登录失败（未成功进入登录后页面），可能是用户名或密码错误。')
