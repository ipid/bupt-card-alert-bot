__all__ = ('base_repr', 'base_eq', 'base_le', 'base_to_json', 'base_from_json')
from typing import Dict, Any, Type, TypeVar

T = TypeVar('T')

def base_repr(popo) -> str:
    props = ', '.join(f'{x} = {getattr(popo, x)}' for x in popo.__slots__)
    return f'<{type(popo).__name__}: {props}>'


def base_eq(popo: T, other: T) -> bool:
    if type(popo) != type(other):
        raise ValueError('POPO 只支持与同类型的对象比较。')

    for prop in popo.__slots__:
        if getattr(popo, prop) != getattr(other, prop):
            return False

    return True


def base_le(popo: T, other: T) -> bool:
    if type(popo) != type(other):
        raise ValueError('POPO 只支持与同类型的对象比较。')

    for prop in popo.__slots__:
        a = getattr(popo, prop)
        b = getattr(other, prop)
        if a == b:
            continue

        return a < b

    return False

def base_to_json(popo: Any):
    return {x: getattr(popo, x) for x in popo.__slots__}


def base_from_json(popo_cls: Type[T], obj: Dict[str, Any]) -> T:
    res = popo_cls()
    for x in popo_cls.__slots__:
        setattr(res, x, obj[x])

    return res
