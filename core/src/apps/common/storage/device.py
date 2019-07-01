from micropython import const
from ubinascii import hexlify

from trezor.crypto import random

from apps.common import storage

# fmt: off
# App:
_APP                = const(0x01)  # app namespace
# Keys:
_DEVICE_ID          = const(0x00)  # bytes
_VERSION            = const(0x01)  # int
_MNEMONIC_SECRET    = const(0x02)  # bytes
_LANGUAGE           = const(0x03)  # str
_LABEL              = const(0x04)  # str
_USE_PASSPHRASE     = const(0x05)  # bool (0x01 or empty)
_HOMESCREEN         = const(0x06)  # bytes
_NEEDS_BACKUP       = const(0x07)  # bool (0x01 or empty)
_FLAGS              = const(0x08)  # int
_U2F_COUNTER        = const(0x09)  # int
_PASSPHRASE_SOURCE  = const(0x0A)  # int
_UNFINISHED_BACKUP  = const(0x0B)  # bool (0x01 or empty)
_AUTOLOCK_DELAY_MS  = const(0x0C)  # int
_NO_BACKUP          = const(0x0D)  # bool (0x01 or empty)
_MNEMONIC_TYPE      = const(0x0E)  # int
_ROTATION           = const(0x0F)  # int
# fmt: on

HOMESCREEN_MAXSIZE = 16384


def is_version_stored() -> bool:
    return bool(storage._get(_APP, _VERSION))


def get_version() -> bool:
    return storage._get(_APP, _VERSION)


def set_version(version: bytes) -> bool:
    return storage._set(_APP, _VERSION, version)


def _new_device_id() -> str:
    return hexlify(random.bytes(12)).decode().upper()


def get_device_id() -> str:
    dev_id = storage._get(_APP, _DEVICE_ID, True)  # public
    if not dev_id:
        dev_id = _new_device_id().encode()
        storage._set(_APP, _DEVICE_ID, dev_id, True)  # public
    return dev_id.decode()


def get_rotation() -> int:
    rotation = storage._get(_APP, _ROTATION, True)  # public
    if not rotation:
        return 0
    return int.from_bytes(rotation, "big")


def get_label() -> str:
    label = storage._get(_APP, _LABEL, True)  # public
    if label is None:
        return None
    return label.decode()


def get_mnemonic_secret() -> bytes:
    return storage._get(_APP, _MNEMONIC_SECRET)


def get_mnemonic_type() -> int:
    return storage._get_uint8(_APP, _MNEMONIC_TYPE)


def has_passphrase() -> bool:
    return storage._get_bool(_APP, _USE_PASSPHRASE)


def get_homescreen() -> bytes:
    return storage._get(_APP, _HOMESCREEN, True)  # public


def store_mnemonic_secret(
    secret: bytes,
    mnemonic_type: int,
    needs_backup: bool = False,
    no_backup: bool = False,
) -> None:
    storage.set_current_version()
    storage._set(_APP, _MNEMONIC_SECRET, secret)
    storage._set_uint8(_APP, _MNEMONIC_TYPE, mnemonic_type)
    storage._set_true_or_delete(_APP, _NO_BACKUP, no_backup)
    if not no_backup:
        storage._set_true_or_delete(_APP, _NEEDS_BACKUP, needs_backup)


def needs_backup() -> bool:
    return storage._get_bool(_APP, _NEEDS_BACKUP)


def set_backed_up() -> None:
    storage._delete(_APP, _NEEDS_BACKUP)


def unfinished_backup() -> bool:
    return storage._get_bool(_APP, _UNFINISHED_BACKUP)


def set_unfinished_backup(state: bool) -> None:
    storage._set_bool(_APP, _UNFINISHED_BACKUP, state)


def no_backup() -> bool:
    return storage._get_bool(_APP, _NO_BACKUP)


def get_passphrase_source() -> int:
    b = storage._get(_APP, _PASSPHRASE_SOURCE)
    if b == b"\x01":
        return 1
    elif b == b"\x02":
        return 2
    else:
        return 0


def load_settings(
    label: str = None,
    use_passphrase: bool = None,
    homescreen: bytes = None,
    passphrase_source: int = None,
    display_rotation: int = None,
) -> None:
    if label is not None:
        storage._set(_APP, _LABEL, label.encode(), True)  # public
    if use_passphrase is not None:
        storage._set_bool(_APP, _USE_PASSPHRASE, use_passphrase)
    if homescreen is not None:
        if homescreen[:8] == b"TOIf\x90\x00\x90\x00":
            if len(homescreen) <= HOMESCREEN_MAXSIZE:
                storage._set(_APP, _HOMESCREEN, homescreen, True)  # public
        else:
            storage._set(_APP, _HOMESCREEN, b"", True)  # public
    if passphrase_source is not None:
        if passphrase_source in (0, 1, 2):
            storage._set(_APP, _PASSPHRASE_SOURCE, bytes([passphrase_source]))
    if display_rotation is not None:
        if display_rotation not in (0, 90, 180, 270):
            raise ValueError(
                "Unsupported display rotation degrees: %d" % display_rotation
            )
        else:
            storage._set(
                _APP, _ROTATION, display_rotation.to_bytes(2, "big"), True
            )  # public


def get_flags() -> int:
    b = storage._get(_APP, _FLAGS)
    if b is None:
        return 0
    else:
        return int.from_bytes(b, "big")


def set_flags(flags: int) -> None:
    b = storage._get(_APP, _FLAGS)
    if b is None:
        b = 0
    else:
        b = int.from_bytes(b, "big")
    flags = (flags | b) & 0xFFFFFFFF
    if flags != b:
        storage._set(_APP, _FLAGS, flags.to_bytes(4, "big"))


def get_autolock_delay_ms() -> int:
    b = storage._get(_APP, _AUTOLOCK_DELAY_MS)
    if b is None:
        return 10 * 60 * 1000
    else:
        return int.from_bytes(b, "big")


def set_autolock_delay_ms(delay_ms: int) -> None:
    if delay_ms < 60 * 1000:
        delay_ms = 60 * 1000
    storage._set(_APP, _AUTOLOCK_DELAY_MS, delay_ms.to_bytes(4, "big"))


def next_u2f_counter() -> int:
    return storage._next_counter(_APP, _U2F_COUNTER, True)  # writable when locked


def set_u2f_counter(count: int) -> None:
    storage._set_counter(_APP, _U2F_COUNTER, count, True)  # writable when locked
