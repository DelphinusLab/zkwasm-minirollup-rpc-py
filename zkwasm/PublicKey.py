from .Point import Point


class PublicKey:
    def __init__(self, key):
        self.key = key

    @staticmethod
    def from_private_key(pk):
        return PublicKey(Point.base().mul(pk.key))
