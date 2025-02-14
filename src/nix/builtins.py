import nix


def imp(path: str):
    return nix.eval(f'import {path}')
