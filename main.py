import argparse
import logging as pymodule_logging
import random
import string

from bupt_card_alert_bot import *

# 初始化基础部件
logger = pymodule_logging.getLogger('bupt_card_alert_bot')
initialize_logger(logger)
argp = argparse.ArgumentParser(description='Send alert with Telegram Bot when new transaction is detected.')
argp.add_argument('--deploy', action='store_true', help='Deploy telegram bot')
argp.add_argument('--debug', action='store_true',
                  help='Turn on debug mode for development. Some behavior changes.')
sess = requests.Session()

# 初始化当前应用中的类
sess_keep = SessionKeeper(sess)
config_dao = ConfigDao()
trans_dao = TransactionDao()
vpc = VpnClient(sess_keep)
ecc = EcardClient(sess_keep)
state_dao = StateDao()
tgbot = TgBotClient(
    bot_token=config_dao['bot.api-token'],
    proxy_url=config_dao['proxy.url'],
)

# 记录已经发送过通知的 Transaction（消费记录），初始为 None
trans_log = set()


# --- 以下定义各工具函数
def vpn_ecard_login() -> None:
    """
    调用 VpnClient 与 EcardClient 类，使其处于已登录状态。
    :return: None
    """
    vpc.login(
        username=config_dao['vpn.username'],
        password=config_dao['vpn.password'],
    )

    ecc.goto_login_page()
    ecc.login(
        username=config_dao['ecard.username'],
        password=config_dao['ecard.password'],
    )


def print_user_info() -> None:
    """
    打印用户的姓名、学号等信息。
    通过获取个人信息，验证 vpn、ecard、tgbot 等配置是否正确。
    :return: None
    """
    ecc.goto_personal_info_page()
    user_info = ecc.parse_personal_info()
    logger.info(
        f'Fetching transactions of current user:\n'
        f'    Name: {user_info.name}\n'
        f'    Id: {user_info.id}\n'
        f'    Role: {user_info.role}\n'
    )


def gc_trans_log(lookup_timedelta_days: int) -> None:
    """
    清除 trans_log 中旧的交易记录。
    :param lookup_timedelta_days: 在 ecard 网站上查询时，最大的“起始时间”距离今天的天数
    :return: None
    """

    # TODO: 实现 trans_log 的垃圾回收逻辑
    pass


# --- 以下为主程序的不同部分
def deploy_bot() -> None:
    """
    部署 Telegram Bot。
    :return: None
    """
    logger.info(f'Deploying bot: @{tgbot.get_bot_name()}')

    # 如果已部署，则提醒用户
    if state_dao['tg_deployed']:
        logger.info('The bot is already deployed. However you can overwrite previous deployment.\n')

    # 随机生成若干位数的“部署命令”。
    trigger_cmd = DEFAULT_DEPLOY_COMMAND + ' ' + ''.join(
        random.choices(string.ascii_letters + string.digits, k=DEPLOY_TRIGGER_STR_LEN))
    logger.debug('Trigger command generated: ' + trigger_cmd)

    # 轮询等待用户发送信息；
    # 当用户给 Bot 发送一模一样的指令时，将发送消息所在的 Chat 的 chat_id 记录下来。
    print('Now send the following command to your Telegram Bot:\n')
    print(trigger_cmd + '\n\n')
    print(f'Please send the text within {DEFAULT_TG_POLL_TIMEOUT} seconds.')

    chat_id = tgbot.wait_for_specific_message(trigger_cmd)
    if chat_id is not None:
        state_dao['tg_deployed'] = True
        state_dao['tg_chat_id'] = chat_id

        tgbot.send_message(chat_id, '[INFO] Bot 成功部署。')
        logger.info(f'Telegram is successfully deployed. Chat id: {chat_id}')
    else:
        # “等待指定消息”超时，未获取到 chat_id
        logger.warning('Failed to receive the command above. Advise:')
        print('1) Ensure you send exactly the same text to the bot.')
        print('''2) Double-check whether your api token corresponds to your bot's name.''')


def server(debug_mode: bool) -> None:
    """
    服务器模式。该模式下本应用长时间运行。
    TODO: 处理第三方库产生的异常
    :return: None
    """

    # trans_log 的值需要被修改
    global trans_log

    logger.debug('running server')

    # 如果 Telegram Bot 没有部署则退出
    if not state_dao['tg_deployed']:
        logger.error('Telegram Bot is not yet deployed. '
                     'Please use option `--deploy` to deploy your bot.\nExit...')
        exit(1)

    # 登录 vpn 和 ecard
    vpn_ecard_login()

    # 通过获取个人信息，验证 vpn、ecard、tgbot 等配置是否正确
    # 如果配置错误，将无法正确获取个人信息
    print_user_info()
    logger.info(f'Bot username: @{tgbot.get_bot_name()}')

    # 通知用户服务器已运行
    tgbot.send_message(state_dao['tg_chat_id'], '[INFO] 服务器开始运行')

    # 循环获取消费记录，并通过 Bot 发送给用户
    logger.info('Begin main loop...')
    while True:
        logger.debug('开始一次新循环')

        # 发送请求，查询消费记录
        ecc.goto_consume_info_page()
        ecc.lookup_consume_info(
            lookup_date=get_begin_end_date(DEFAULT_ECARD_TIMEDELTA),
            with_sort_button=not ecc.is_sort_button_desc(),
        )
        current_trans = ecc.parse_consume_info()

        # 如果该循环第一次运行，就将获取到的消费记录直接存起来
        # 在调试模式下则不进行此操作（因此可以查看最初的 10 条记录）
        if not debug_mode and len(trans_log) == 0:
            trans_log = current_trans.copy()

        new_trans = sorted(
            # 过滤掉已经发送过通知的消费记录
            current_trans - trans_log,

            # 按照消费时间排序，如果一样，则余额大的在前
            key=lambda x: (x.op_timestamp, -x.balance))
        logger.debug(f'获得了 {len(current_trans)} 条交易记录, 其中 {len(new_trans)} 条为新记录')

        # 为了防止洗澡等小额记录过多，合并细小的消费记录
        # 为了不影响排重逻辑，应在服务器端存储原始消费记录，但是将合并的消费记录发送给用户
        combined_trans = combine_continuous_small_transactions(new_trans)

        # 将多条新的消费记录发送给用户
        # 使用 set 储存的 Transaction 可能是无序的，因此需要排序
        for trans in combined_trans:
            logger.debug(f'发送 {trans.op_datetime} 的消费记录')
            tgbot.send_message(state_dao['tg_chat_id'], '\n'.join((
                f'<b>校园卡支出 {trans.trans_amount:.2f} 元</b>',
                f'',
                f'<b>时间：</b>{trans.op_datetime}',
                f'<b>消费类别：</b>{trans.category}',
                f'<b>位置：</b>{trans.location}',
                f'',
                f'<b>钱包余额：</b>{trans.balance:.2f} 元',
            )))

        # 将新获取的、合并后的 Transaction 记入 trans_log 中
        trans_log.update(current_trans)
        logger.debug(f'trans_log 元素个数: {len(trans_log)}')

        # 循环不能高速执行，否则会遭到学校反爬
        time.sleep(DEFAULT_MAIN_LOOP_INTERVAL)

        # 清理旧的消费记录缓存
        gc_trans_log(DEFAULT_ECARD_TIMEDELTA)


# --- 以下为主函数
def main():
    args = argp.parse_args()
    try:
        if args.deploy:
            # Telegram Bot 部署模式
            deploy_bot()
        else:
            # 服务器模式
            server(args.debug)
    except KeyboardInterrupt:
        # 用户按下了 Ctrl+C
        pass
    except Exception as e:
        logger.exception(e)


if __name__ == '__main__':
    main()
