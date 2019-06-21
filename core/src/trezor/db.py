from ubinascii import hexlify

from trezor import io
from trezor.crypto import chacha20poly1305, hmac, random
from trezor.crypto.hashlib import sha256

from apps.common import cbor

MAGIC = b"TRDB"
VERSION = 1


class DB:
    def __init__(self, name: str):
        self.sd = io.SDCard()
        self.sd.power(True)
        self.fs = io.FatFS()
        self.fs.mount()
        try:
            self.fs.mkdir("/trezor")
        except OSError:
            pass
        self.dir = "/trezor/%s" % name
        try:
            self.fs.mkdir(self.dir)
        except OSError:
            pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.fs.unmount()
        self.sd.power(False)

    def _key_to_fname(self, key: bytes) -> str:
        h = hexlify(hmac.new(key, MAGIC, sha256).digest()).decode()
        fn = "%s/%s.trdb" % (self.dir, h)
        return fn

    def _derive_enckey(self, fn: str) -> bytes:
        # TODO: derive symmetric key from master seed
        return sha256(fn).digest()

    def get(self, key: bytes) -> object:
        fn = self._key_to_fname(key)
        try:
            s = self.fs.stat(fn)
        except OSError:
            raise KeyError
        buf = bytearray(s[0])
        with self.fs.open(fn, "r") as f:
            f.read(buf)
        if buf[:4] != MAGIC:
            raise ValueError("Invalid magic")
        if buf[4:8] != VERSION.to_bytes(4, "big"):
            raise ValueError("Invalid version")
        enckey = self._derive_enckey(fn)
        nonce = buf[8:20]
        ctx = chacha20poly1305(enckey, nonce)
        ctx.auth(fn)
        dec = ctx.decrypt(buf[20:-16])
        tag = ctx.finish()
        if tag != buf[-16:]:
            raise ValueError("Invalid MAC")
        data = cbor.decode(dec)
        return data

    def put(self, key: bytes, data: object) -> None:
        fn = self._key_to_fname(key)
        enckey = self._derive_enckey(fn)
        nonce = random.bytes(12)
        ctx = chacha20poly1305(enckey, nonce)
        ctx.auth(fn)
        enc = ctx.encrypt(cbor.encode(data))
        tag = ctx.finish()
        with self.fs.open(fn, "w") as f:
            f.write(MAGIC)
            f.write(VERSION.to_bytes(4, "big"))
            f.write(nonce)
            f.write(enc)
            f.write(tag)

    def delete(self, key: bytes) -> None:
        fn = self._key_to_fname(key)
        self.fs.unlink(fn)
