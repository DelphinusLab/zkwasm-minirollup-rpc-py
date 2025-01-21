import hashlib
import os

from .CurveField import CurveField
from .Point import Point
from .PublicKey import PublicKey


class PrivateKey:
    def __init__(self, key):
        self.key = key
        self.pubk = None

    @staticmethod
    def random():
        return PrivateKey(CurveField(int.from_bytes(os.urandom(32), "big")))

    @staticmethod
    def from_string(s):
        return PrivateKey(CurveField(int(s, 16)))

    def to_string(self):
        return hex(self.key.v)[2:]

    def r(self):
        return CurveField(int.from_bytes(os.urandom(32), "big"))

    @property
    def public_key(self):
        if not self.pubk:
            self.pubk = PublicKey.from_private_key(self)
        return self.pubk

    def sign(self, message):
        Ax = self.public_key.key.x
        r = self.r()
        R = Point.base().mul(r)
        Rx = R.x

        content = []
        content.extend(Rx.v.to_bytes(32, "big"))
        content.extend(Ax.v.to_bytes(32, "big"))
        content.extend(message)

        H = int(hashlib.sha256(bytearray(content)).hexdigest(), 16)
        S = r.add(self.key.mul(CurveField(H)))

        return [[R.x.v, R.y.v], S.v]
