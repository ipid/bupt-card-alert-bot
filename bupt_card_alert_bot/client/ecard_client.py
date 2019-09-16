'''
    本文件引入 EcardSpider 类。
    该类负责向后端（webvpn-ecard）发送「登录」、「查询消费记录」等请求。
    该类初始化时需要一个（临时性的）vpn.bupt.edu.cn 的 Cookie。
'''

__all__ = ('EcardClient',)

import logging as pym_logging
import re
from typing import Optional, Tuple, Set, Dict, Any

from bs4 import BeautifulSoup

from ..exceptions import AppFatalError
from ..popo import SessionKeeper, EcardUserInfo, Transaction
from ..util import get_begin_end_date, parse_ecard_date, log_resp

logger = pym_logging.getLogger('bupt_card_alert_bot.client.ecard_client')

# 匹配 HTML 的标签（tag），及其周围的空白符；将多个标签视为一个，以方便替换
RE_HTML_TAG = re.compile(r'(<[^>]*>(\s|&nbsp;?)*)+')

# 消费记录表格应该有 7 列
TR_DATA_EXPECTED_LENGTH = 7


class EcardClient:
    """
    ecard.bupt.edu.cn 的客户端。

    该类遵守类似无头浏览器（如 Selenium）的逻辑。

    在获取某个页面上的信息时，需先调用以 goto/lookup 开头的方法（这类方法改变类的状态），
    再调用 parse 开头的方法。
    """
    __slots__ = ('sess_keep', 'last_soup')

    def __init__(self, sess_keep: SessionKeeper) -> None:
        if sess_keep.sess is None:
            raise ValueError('sess_keep 内必须有已初始化的 Session。')

        self.sess_keep = sess_keep

    def goto(self, url: str, validation: Optional[str] = None) -> Any:
        """
        向 url 发送 get 请求，并将获取到的 HTML 解析后存入本类中。

        为验证该 GET 请求是否成功，可通过 validation 参数提供一段文字，
        如果在服务器的返回中未找到此段文字（或状态码不为 200），则认为请求失败。
        :param url: URL
        :param validation: 为验证该 GET 请求是否成功
        :return: requests.get() 的返回值，原始请求结果
        """

        sess = self.sess_keep.sess
        resp = sess.get(url)
        if resp.status_code != 200:
            log_resp(logger, resp)
            raise AppFatalError(f'无法获取 URL {url}')
        if validation is not None and validation not in resp.text:
            log_resp(logger, resp)
            raise AppFatalError(f'指定的内容「{validation}」无法在 {url} 中找到。')

        self.last_soup = BeautifulSoup(resp.text, 'html.parser')
        return resp

    def goto_login_page(self) -> None:
        self.goto('https://vpn.bupt.edu.cn/http/ecard.bupt.edu.cn/Login.aspx', '用户登录</a>')

    def goto_consume_info_page(self) -> None:
        self.goto('https://vpn.bupt.edu.cn/http/ecard.bupt.edu.cn/User/ConsumeInfo.aspx',
                  '''User/ConsumeInfo.aspx'>消费信息查询</a>''')

    def goto_personal_info_page(self) -> None:
        self.goto('https://vpn.bupt.edu.cn/http/ecard.bupt.edu.cn/User/baseinfo.aspx', '个 人 基 本 信 息')

    def login(self, username: str, password: str) -> None:
        """
        模拟登录 ecard 网站。
        :param username: 用户名
        :param password: 密码1
        :return: None
        """
        logger.debug('登录 Ecard')
        sess = self.sess_keep.sess

        # 填写表单
        form = self.__get_post_body_of_form()

        form['txtUserName'] = username
        form['txtPassword'] = password
        form['__EVENTTARGET'] = 'btnLogin'

        resp = sess.post(
            'https://vpn.bupt.edu.cn/http/ecard.bupt.edu.cn/Login.aspx',
            data=form)

        if '账户或密码错误' in resp.text:
            raise AppFatalError('用户提供的 Ecard 用户名或密码错误，无法登录 Ecard 网站。')

        if not resp.url.endswith('Index.aspx'):
            log_resp(logger, resp)
            raise AppFatalError('无法登录 Ecard 网站。')

        self.last_soup = BeautifulSoup(resp.text, 'html.parser')

    def parse_personal_info(self) -> EcardUserInfo:
        """
        从本类的状态中解析 Ecard 个人信息。
        :return: EcardUserInfo 对象
        """
        soup = self.last_soup
        ecard_info = EcardUserInfo(
            id=soup.find(id='ContentPlaceHolder1_txtOutID').string,
            name=soup.find(id='ContentPlaceHolder1_txtUserName').string,
            role=soup.find(id='ContentPlaceHolder1_txtCardSF').string,
        )

        return ecard_info

    def lookup_consume_info(self, with_sort_button: bool = False,
                            lookup_date: Optional[Tuple[str, str]] = None) -> None:
        """
        向查询消费记录的接口发送 POST 请求，以获取含消费记录的页面。
        获取到的 HTML 将在解析后存入本类中。

        :param with_sort_button: 该网站按下“箭头”按钮时会发出 POST 请求。如果为 True，将在 POST 同时模拟按下该按钮。
        :param lookup_date: 网站上的参数“起始日期”和“截止日期”，形如 2000-01-01
        :return: None
        """
        logger.debug(f'lookup_consume_info(使用排序按钮={with_sort_button}, 查询日期={lookup_date})')

        # 填写查询表单（以下内容为通过抓包获取）
        form = self.__get_post_body_of_form()
        form['__EVENTARGUMENT'] = ''

        # 当 with_sort_button 时，只需略微修改表单
        if with_sort_button:
            form['__EVENTTARGET'] = 'ctl00$ContentPlaceHolder1$gridView$ctl01$SortBt'
            if 'ctl00$ContentPlaceHolder1$btnSearch' in form:
                del form['ctl00$ContentPlaceHolder1$btnSearch']
        else:
            form['__EVENTTARGET'] = ''
            form['ctl00$ContentPlaceHolder1$btnSearch'] = '查  询'

        if lookup_date is None:
            lookup_date = get_begin_end_date()
        form['ctl00$ContentPlaceHolder1$txtStartDate'] = lookup_date[0]
        form['ctl00$ContentPlaceHolder1$txtEndDate'] = lookup_date[1]
        form['ctl00$ContentPlaceHolder1$rbtnType'] = '0'

        sess = self.sess_keep.sess
        resp = sess.post('https://vpn.bupt.edu.cn/http/ecard.bupt.edu.cn/User/ConsumeInfo.aspx',
                         data=form)
        if '''User/ConsumeInfo.aspx'>消费信息查询</a>''' not in resp.text:
            log_resp(logger, resp)
            raise AppFatalError('消费信息查询失败')

        self.last_soup = BeautifulSoup(resp.text, 'html.parser')

    def parse_consume_info(self) -> Set[Transaction]:
        """
        从本类的状态中解析个学号、姓名等个人信息。
        :return: set 容器，元素为 Transaction 对象
        """

        form1 = self.last_soup.find(id='form1')
        info_table = form1.find(id='ContentPlaceHolder1_gridView')
        if info_table is None:
            logger.debug(f'form1 的 HTML: {str(info_table)}')
            raise AppFatalError('找不到存放消费记录的 <table>。')
        if 'class="gvNoRecords"' in str(info_table):
            # 网页弹出了提示“未查询到记录！”
            return set()

        res = set()
        # 遍历存放消费记录的 <table> 的每一个 <tr>
        for tr in info_table.select('tr:not(.HeaderStyle)'):
            # 将多余的 HTML 标签替换为换行符，再将头尾换行符去掉，最后按行分割为字符串数组
            tr_data = RE_HTML_TAG.sub('\n', str(tr)).strip().split('\n')
            if tr_data == [''] or len(tr_data) == 0:
                # 空行则跳过
                continue

            if len(tr_data) != TR_DATA_EXPECTED_LENGTH:
                logger.debug(f'消费记录爆炸。res = {res}\ninfo_table = {str(info_table)}\ntr_data = {tr_data}')
                raise AppFatalError(f'消费记录的列数为 {len(tr_data)}，'
                               f'与预设值 {TR_DATA_EXPECTED_LENGTH} 不同，可能是解析代码出错。')

            # 将原始数据存入 Transaction 对象，以方便使用
            # 此处将对应关系一行行写出，灵活性更强
            transaction = Transaction(
                op_datetime=tr_data[0],
                category=tr_data[1],
                trans_amount=float(tr_data[2]),
                balance=float(tr_data[3]),
                location=tr_data[6],
                # 将日期解析成时间戳保存
                op_timestamp=parse_ecard_date(tr_data[0]),
            )

            res.add(transaction)

        return res

    def is_sort_button_desc(self) -> bool:
        """
        在已进入“xx信息查询”页面的状态下，判断“操作时间”上的按钮是否处于降序状态。
        :return: True 表示当前操作时间按降序排列
        """

        btn = self.last_soup.find(id='ContentPlaceHolder1_gridView_SortBt')
        if btn is None:
            logger.debug(f'无法找到箭头按钮。self.last_soup = {str(self.last_soup)}')
            raise AppFatalError('没找到箭头按钮（SortBt）。')

        class_name = btn.attrs['class'][0]
        if class_name != 'SortBt_Desc' and class_name != 'SortBt_Asc':
            logger.debug(f'btn = {str(btn)}\nclass_name = {class_name}')
            raise AppFatalError('箭头按钮（SortBt）的 class 属性异常。')

        return btn.attrs['class'] == 'SortBt_Desc'

    def __get_post_body_of_form(self) -> Dict[str, str]:
        """
        Aspx 提交表单时必须提交 __VIEWSTATE，该值在正常访问时通过 hidden <input> 传递给浏览器。
        本方法可从 self.last_soup 中获取到类似的必填属性值。然而，剩余的内容仍要自己填写。

        :return: dict，表示一个表单
        """
        form = dict()

        for i in self.last_soup.form.find_all(attrs={'name': True}):
            form[i.attrs['name']] = i.attrs['value'] if 'value' in i.attrs else ''

        return form
