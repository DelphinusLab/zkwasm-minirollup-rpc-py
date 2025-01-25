from .CurveField import CurveField
from .Field import Field
from .Point import Point
from .PrivateKey import PrivateKey
from .poseidon import poseidon


def big_endian_hex_to_int(hex_string):
    if hex_string.startswith("0x"):
        hex_string = hex_string[2:]
    if len(hex_string) % 2 != 0:
        hex_string = "0" + hex_string
    return int(hex_string, 16)


def little_endian_hex_to_int(hex_string):
    if hex_string.startswith("0x"):
        hex_string = hex_string[2:]
    if len(hex_string) % 2 != 0:
        hex_string = "0" + hex_string
    reversed_hex = "".join(
        [hex_string[i: i + 2] for i in range(len(hex_string) - 2, -1, -2)]
    )
    return int(reversed_hex, 16)


def u8_to_hex(u8_array: bytearray) -> str:
    return "".join(f"{byte:02x}" for byte in u8_array)


def bn_to_hex_le(n: int, length: int = 32) -> str:
    bytes_le = n.to_bytes(length, byteorder="little", signed=False)
    return u8_to_hex(bytes_le)


class LeHexInt:
    def __init__(self, hexstr):
        self.hexstr = hexstr

    def to_int(self):
        return little_endian_hex_to_int(self.hexstr)

    def to_u64_array(self):
        values = [0] * 4
        num = self.to_int()
        for i in range(4):
            values[i] = num % (1 << 64)
            num >>= 64
        return values


def verify_sign(msg, pkx, pky, rx, ry, s):
    l = Point.base().mul(CurveField(s.to_int()))
    pkey = Point(CurveField(pkx.to_int()), CurveField(pky.to_int()))
    r = Point(CurveField(rx.to_int()), CurveField(ry.to_int())).add(
        pkey.mul(CurveField(msg.to_int()))
    )
    negr = Point(r.x.neg(), r.y)
    return l.add(negr).is_zero()


def sign(cmd, prikey):
    pkey = PrivateKey.from_string(prikey)
    r = pkey.r()
    R = Point.base().mul(r)

    # Calculate H using poseidon hash
    fvalues = []
    h = 0
    i = 0
    while i < len(cmd):
        v = 0
        for j in range(3):
            if i + j < len(cmd):
                v += cmd[i + j] << (64 * j)
                h += cmd[i + j] << (64 * (j + i))
        i += 3
        fvalues.append(Field(v))

    H = poseidon(fvalues).v
    hbn = H
    msgbn = h


    S = r.add(pkey.key.mul(CurveField(hbn)))
    pubkey = pkey.public_key

    data = {
        'msg': bn_to_hex_le(msgbn, len(cmd) * 8),
        'hash': bn_to_hex_le(hbn),
        'pkx': bn_to_hex_le(pubkey.key.x.v),
        'pky': bn_to_hex_le(pubkey.key.y.v),
        'sigx': bn_to_hex_le(R.x.v),
        'sigy': bn_to_hex_le(R.y.v),
        'sigr': bn_to_hex_le(S.v),
    }
    return data


def query(prikey):
    pkey = PrivateKey.from_string(prikey)
    pubkey = pkey.public_key
    data = {
        "pkx": bn_to_hex_le(pubkey.key.x.v),
    }
    return data


def get_pid(prikey):
    pkey = PrivateKey.from_string(prikey)
    pubkey = pkey.public_key
    pid_key = bn_to_hex_le(pubkey.key.x.v)
    pid_all = LeHexInt(pid_key).to_u64_array()
    pid = pid_all[1], pid_all[2]
    return pid
