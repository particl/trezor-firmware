from micropython import const

from trezor.crypto import slip39

from apps.common import storage

# Mnemonics stored during SLIP-39 recovery process.
# App:
_SLIP39_MNEMONICS = const(0x03)
# Keys:
# Each mnemonic is stored under key = index.


def set(index: int, mnemonic: str):
    storage._set(_SLIP39_MNEMONICS, index, mnemonic.encode())


def get(index: int) -> str:
    m = storage._get(_SLIP39_MNEMONICS, index)
    if m:
        return m.decode()
    return False


def fetch() -> list:
    mnemonics = []
    for index in range(0, slip39.MAX_SHARE_COUNT):
        m = get(index)
        if m:
            mnemonics.append(m)
    return mnemonics


def delete():
    for index in (0, slip39.MAX_SHARE_COUNT):
        storage._delete(_SLIP39_MNEMONICS, index)
