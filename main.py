import requests

from bupt_card_alert_bot import *

sess = requests.Session()
sess_keep = SessionKeeper(sess)
vpc = VpnClient(sess_keep)

config_dao = ConfigDao()
vpc.login(
    username=config_dao['vpn.username'],
    password=config_dao['vpn.password'],
)

ecc = EcardClient(sess_keep)
ecc.goto_login_page()
ecc.login(
    username=config_dao['ecard.username'],
    password=config_dao['ecard.password'],
)
ecc.goto_personal_info_page()
print(ecc.parse_personal_info())

ecc.goto_consume_info_page()

ecc.lookup_consume_info(
    with_sort_button=not ecc.is_sort_button_desc()
)
print()
