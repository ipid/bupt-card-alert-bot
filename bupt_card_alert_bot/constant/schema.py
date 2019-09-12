"""
静态配置文件的 JSON Schema。
用于验证该配置文件格式是否正确。
"""
CONFIG_SCHEMA = {
    '$schema': 'http://json-schema.org/schema#',
    'type': 'object',
    'properties': {
        'vpn.username': {'type': 'string', 'minLength': 1},
        'vpn.password': {'type': 'string', 'minLength': 1},
        'ecard.username': {'type': 'string', 'minLength': 1},
        'ecard.password': {'type': 'string', 'minLength': 1},
        'bot.api-token': { 'type': 'string', 'minLength': 1},
        'proxy.url': { 'type': 'string', 'minLength': 1},
        'proxy.username': { 'type': 'string', 'minLength': 1},
        'proxy.password': { 'type': 'string', 'minLength': 1},
    },
    'required': [
        'vpn.username',
        'vpn.password',
        'ecard.username',
        'ecard.password',
        'bot.api-token',
    ],
}
