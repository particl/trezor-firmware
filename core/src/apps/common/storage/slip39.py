from micropython import const

from apps.common import storage
from apps.common.storage import slip39_mnemonics

# fmt: off
# App:
_SLIP39                    = const(0x02)  # SLIP-39 namespace
# Keys:
_SLIP39_IN_PROGRESS        = const(0x00)  # bool
_SLIP39_IDENTIFIER         = const(0x01)  # bytes
_SLIP39_THRESHOLD          = const(0x02)  # int
_SLIP39_REMAINING          = const(0x03)  # int
_SLIP39_WORDS_COUNT        = const(0x04)  # int
_SLIP39_ITERATION_EXPONENT = const(0x05)  # int
# fmt: on


def set_in_progress(val: bool):
    storage._set_bool(_SLIP39, _SLIP39_IN_PROGRESS, val)


def is_in_progress():
    return storage._get_bool(_SLIP39, _SLIP39_IN_PROGRESS)


def set_identifier(identifier: int):
    storage._set_uint16(_SLIP39, _SLIP39_IDENTIFIER, identifier)


def get_identifier() -> int:
    return storage._get_uint16(_SLIP39, _SLIP39_IDENTIFIER)


def set_threshold(threshold: int):
    storage._set_uint8(_SLIP39, _SLIP39_THRESHOLD, threshold)


def get_threshold() -> int:
    return storage._get_uint8(_SLIP39, _SLIP39_THRESHOLD)


def set_remaining(remaining: int):
    storage._set_uint8(_SLIP39, _SLIP39_REMAINING, remaining)


def get_remaining() -> int:
    return storage._get_uint8(_SLIP39, _SLIP39_REMAINING)


def set_words_count(count: int):
    storage._set_uint8(_SLIP39, _SLIP39_WORDS_COUNT, count)


def get_words_count() -> int:
    return storage._get_uint8(_SLIP39, _SLIP39_WORDS_COUNT)


def set_iteration_exponent(exponent: int):
    storage._set_uint8(_SLIP39, _SLIP39_ITERATION_EXPONENT, exponent)


def get_iteration_exponent() -> int:
    return storage._get_uint8(_SLIP39, _SLIP39_ITERATION_EXPONENT)


def delete_progress():
    storage._delete(_SLIP39, _SLIP39_IN_PROGRESS)
    storage._delete(_SLIP39, _SLIP39_REMAINING)
    storage._delete(_SLIP39, _SLIP39_THRESHOLD)
    storage._delete(_SLIP39, _SLIP39_WORDS_COUNT)
    slip39_mnemonics.delete()
