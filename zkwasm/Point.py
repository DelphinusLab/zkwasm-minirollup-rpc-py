from .CurveField import CurveField
from .Field import Field
from .constants import constants


class Point:
    def __init__(self, x, y):
        self.x = x if isinstance(x, Field) else Field(x)
        self.y = y if isinstance(y, Field) else Field(y)

    @property
    def zero(self):
        return Point(0, 1)

    def is_zero(self):
        return self.x.v == 0 and self.y.v == 1

    @staticmethod
    def base():
        gX = constants["gX"]
        gY = constants["gY"]
        return Point(gX, gY)

    def add(self, p):
        u1 = self.x
        v1 = self.y
        u2 = p.x
        v2 = p.y

        u3_m = u1.mul(v2).add(v1.mul(u2))
        u3_d = constants["d"].mul(u1).mul(u2).mul(v1).mul(v2).add(Field(1))
        u3 = u3_m.div(u3_d)

        v3_m = v1.mul(v2).sub(constants["a"].mul(u1).mul(u2))
        v3_d = Field(1).sub(constants["d"].mul(u1).mul(u2).mul(v1).mul(v2))
        v3 = v3_m.div(v3_d)

        return Point(u3, v3)

    def mul(self, p):
        if isinstance(p, CurveField):
            p = p.v
        elif not isinstance(p, int):
            p = int(p)

        t = p
        sum = self.zero
        acc = self

        while t != 0:
            if t % 2 == 1:
                sum = sum.add(acc)
            acc = acc.add(acc)
            t //= 2
        return sum
