import requests

from bupt_card_alert_bot import *

sess = requests.Session()

sess_keep = SessionKeeper(sess)
config_dao = ConfigDao()
trans_dao = TransactionDao()
vpc = VpnClient(sess_keep)
ecc = EcardClient(sess_keep)
state_dao = StateDao()
tgbot = TgBotClient(
    bot_token=config_dao['bot.api-token'],
    state_dao=state_dao,
    proxy_url=config_dao['proxy.url'],
)

vpc.login(
    username=config_dao['vpn.username'],
    password=config_dao['vpn.password'],
)

ecc.goto_login_page()
ecc.login(
    username=config_dao['ecard.username'],
    password=config_dao['ecard.password'],
)
ecc.goto_personal_info_page()
print(ecc.parse_personal_info())

ecc.goto_consume_info_page()
ecc.lookup_consume_info(
    lookup_date=get_begin_end_date(3),
    with_sort_button=not ecc.is_sort_button_desc(),
)
transactions = set(ecc.parse_consume_info())
trans_dao.store_transactions(transactions)
load_trans = trans_dao.load_transaction_set()
print(f'trans load == store: {transactions == load_trans}')

print(f'''state_dao['tg_deployed'] = {state_dao['tg_deployed']}''')
print(f'''state_dao['tg_chat_id'] = {state_dao['tg_chat_id']}''')
print(tgbot.get_me())
chat_id = tgbot.wait_for_specific_message('/ecard_deploy fuck you', timeout=10)
print(f'chat_id = {chat_id}')
if chat_id is not None:
    tgbot.send_message(chat_id, 'shut up')
