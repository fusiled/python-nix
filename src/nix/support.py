from contextlib import contextmanager

from .expr import Type, Value


def attrsget(attrs: Value, *args) -> [Value]:
    import operator
    match attrs.force_type({Type.attrs, Type.list}):
        case Type.attrs:
            return [attrs.get_attr_byname(a) for a in args]
        case _:
            raise RuntimeError

@contextmanager
def attrswith(attrs: Value, *args):
    yield attrsget(attrs, *args)