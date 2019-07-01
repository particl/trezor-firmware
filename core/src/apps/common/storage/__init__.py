from trezor import config

from apps.common import cache
from apps.common.storage import device, slip39

_FALSE_BYTE = b"\x00"
_TRUE_BYTE = b"\x01"

_STORAGE_VERSION_01 = b"\x01"
_STORAGE_VERSION_CURRENT = b"\x02"


def set_current_version():
    device.set_version(_STORAGE_VERSION_CURRENT)


def is_initialized() -> bool:
    return device.is_version_stored() and not slip39.is_in_progress()


def _set(app: int, key: int, data: bytes, public: bool = False):
    config.set(app, key, data, public)


def _get(app: int, key: int, public: bool = False):
    return config.get(app, key, public)


def _delete(app: int, key: int):
    config.delete(app, key)


def _set_true_or_delete(app: int, key: int, value: bool):
    if value:
        _set_bool(app, key, value)
    else:
        _delete(app, key)


def _set_bool(app: int, key: int, value: bool, public: bool = False) -> None:
    if value:
        _set(app, key, _TRUE_BYTE, public)
    else:
        _set(app, key, _FALSE_BYTE, public)


def _get_bool(app: int, key: int, public: bool = False) -> bool:
    return _get(app, key, public) == _TRUE_BYTE


def _set_uint8(app: int, key: int, val: int):
    _set(app, key, val.to_bytes(1, "big"))


def _get_uint8(app: int, key: int) -> int:
    val = _get(app, key)
    if not val:
        return None
    return int.from_bytes(val, "big")


def _set_uint16(app: int, key: int, val: int):
    _set(app, key, val.to_bytes(2, "big"))


def _get_uint16(app: int, key: int) -> int:
    val = _get(app, key)
    if not val:
        return None
    return int.from_bytes(val, "big")


def _next_counter(app: int, key: int, public: bool = False):
    return config.next_counter(app, key, public)


def _set_counter(app: int, key: int, count: int, public: bool = False) -> None:
    config.set_counter(app, key, count, public)


def wipe():
    config.wipe()
    cache.clear()


def init_unlocked():
    # Check for storage version upgrade.
    version = device.get_version()
    if version == _STORAGE_VERSION_01:
        _migrate_from_version_01()


def _migrate_from_version_01():
    # Make the U2F counter public and writable even when storage is locked.
    # U2F counter wasn't public, so we are intentionally not using storage.device module.
    counter = _get(device._APP, device._U2F_COUNTER)
    if counter is not None:
        device.set_u2f_counter(int.from_bytes(counter, "big"))
        # Delete the old, non-public U2F_COUNTER.
        _delete(device._APP, device._U2F_COUNTER)
    set_current_version()
