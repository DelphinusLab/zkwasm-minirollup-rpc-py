from typing import Union

from .Field import Field


class CurveField:
    def __init__(self, v: Union[int, "Field"]):
        self.modulus = int(
            "2736030358979909402780800718157159386076813972158567259200215660948447373041",
            10,
        )
        if isinstance(v, Field):
            v = v.v  # 假设 Field 类型有 v 属性
        elif isinstance(v, str):  # 如果是字符串，尝试转换为整数
            v = int(v, 10)
        elif not isinstance(v, int):
            raise ValueError("v must be an int or Field")
        self.v = v % self.modulus

    def add(self, f: "CurveField") -> "CurveField":
        return CurveField((self.v + f.v) % self.modulus)

    def mul(self, f: "CurveField") -> "CurveField":
        return CurveField((self.v * f.v) % self.modulus)

    def sub(self, f: "CurveField") -> "CurveField":
        return CurveField((self.v - f.v) % self.modulus)

    def neg(self) -> "CurveField":
        return CurveField(-self.v % self.modulus)

    def div(self, f: "CurveField") -> "CurveField":
        return CurveField((self.v * f.inv().v) % self.modulus)

    def inv(self) -> "CurveField":
        if self.v == 0:
            raise ZeroDivisionError("Cannot calculate the inverse of zero")

        # 扩展欧几里得算法
        newt, t = 1, 0
        newr, r = self.v, self.modulus

        while newr != 0:
            q = r // newr
            t, newt = newt, t - q * newt
            r, newr = newr, r - q * newr

        # 结果可能是负数，确保结果为正数
        return CurveField(t % self.modulus)

    def __repr__(self):
        return f"CurveField({self.v})"
