"""
静态配置文件的 JSON Schema。
用于验证该配置文件格式是否正确。
"""

CONFIG_VALID_PROPS = frozenset((
    # vpn.bupt.edu.cn 的用户名/密码
    'vpn.username',
    'vpn.password',

    # ecard.bupt.edu.cn 的用户名/密码
    'ecard.username',
    'ecard.password',

    # Telegram Bot 的 API Token
    'bot.api-token',

    # 连接 Telegram 服务器所使用的代理
    # 注：访问 webvpn 和 ecard 不支持使用代理
    'proxy.url',
))

CONFIG_SCHEMA = {
    '$schema': 'http://json-schema.org/schema#',
    'type': 'object',
    'properties': {
        'vpn.username': {'type': 'string', 'minLength': 1},
        'vpn.password': {'type': 'string', 'minLength': 1},
        'ecard.username': {'type': 'string', 'minLength': 1},
        'ecard.password': {'type': 'string', 'minLength': 1},
        'bot.api-token': {'type': 'string', 'minLength': 1},
        'proxy.url': {'type': 'string', 'minLength': 1},
    },
    'required': [
        'vpn.username',
        'vpn.password',
        'ecard.username',
        'ecard.password',
        'bot.api-token',
    ],
}