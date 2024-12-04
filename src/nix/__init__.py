from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .expr import Value

from . import support

__all__ = ["util", "store", "expr", "eval", "support"]

_state = None
_store = None


def global_init():
    from .store import Store
    from .expr import State

    global _store, _state
    if _store is None or _state is None:
        _store = Store()
        _state = State([], _store)


def eval(string: str, path: str = ".") -> Value:
    """ Evaluate a Nix expression string into a Value, automatically allocating a state """
    global_init()
    return _state.eval_string(string, path)


def getenv(path: str = "."):
    """
      Instantiate a attributes set that can be used to do anything.
      import is aliased as nimport since 'import' in python is a reserved name
    """
    return eval("builtins // { nimport = builtins.import; }", path)


def lookup_path(path: str):
    if len(path) >= 2 and path[0] == '<' and path[-1] == '>':
        return eval(path)
    raise RuntimeError(f'nix.lookup_path call must be contained with diamond notation. For example \'<nixpkgs>\'. '
                       f'Passed \'{path}\'')
