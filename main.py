import argparse
import logging
import random
import string

from bupt_card_alert_bot import *

# 初始化基础部件
logger = logging.getLogger('')
initialize_logger(logger)
argp = argparse.ArgumentParser(description='Send alert with Telegram Bot when new transaction is detected.')
argp.add_argument('--deploy', action='store_true')
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

# 记录已经发送过通知的 Transaction（消费记录）
trans_log = set()


# --- 以下定义各工具函数
def vpn_ecard_login():
    vpc.login(
        username=config_dao['vpn.username'],
        password=config_dao['vpn.password'],
    )

    ecc.goto_login_page()
    ecc.login(
        username=config_dao['ecard.username'],
        password=config_dao['ecard.password'],
    )


def print_user_info():
    ecc.goto_personal_info_page()
    user_info = ecc.parse_personal_info()
    logger.info(
        f'Fetching transactions for current user:\n'
        f'    Name: {user_info.name}\n'
        f'    Id: {user_info.id}\n'
        f'    Role: {user_info.role}\n'
    )


# --- 以下为主程序的不同部分
def deploy_bot():
    logger.info(f'Deploying bot: @{tgbot.get_bot_name()}')

    if state_dao['tg_deployed']:
        logger.info('The bot is already deployed. However you can overwrite previous deployment.\n')

    trigger_cmd = DEFAULT_DEPLOY_COMMAND + ' ' + ''.join(
        random.choices(string.ascii_letters + string.digits, k=DEPLOY_TRIGGER_STR_LEN))
    logger.debug('Trigger command generated: ' + trigger_cmd)

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
        logger.warning('Failed to receive the command above. Advise:')
        print('1) Ensure you send exactly the same text to the bot.')
        print('''2) Double-check whether your api token corresponds to your bot's name.''')


def server():
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

    # 进入循环
    while True:
        ecc.goto_consume_info_page()
        ecc.lookup_consume_info(
            lookup_date=get_begin_end_date(DEFAULT_ECARD_TIMEDELTA),
            with_sort_button=not ecc.is_sort_button_desc(),
        )
        current_trans = ecc.parse_consume_info()
        # 过滤掉已经发送过通知的消费记录
        new_trans = current_trans - trans_log

        pass


# --- 以下为主函数
def main():
    args = argp.parse_args()
    if args.deploy:
        deploy_bot()
    else:
        server()


if __name__ == '__main__':
    main()
