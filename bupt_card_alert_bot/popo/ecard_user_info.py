__all__ = ('EcardUserInfo',)


class EcardUserInfo:
    __slots__ = ('id', 'name', 'role')

    def __init__(self, id=None, name=None, role=None):
        self.id = id
        self.name = name
        self.role = role

    def __repr__(self):
        return f'<EcardUserInfo id = {self.id}, name = {self.name}, role = {self.role}>'
