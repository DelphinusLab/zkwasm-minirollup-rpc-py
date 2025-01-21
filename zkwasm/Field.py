class Field:
    def __init__(self, v: int):
        self.modulus = int("21888242871839275222246405745257275088548364400416034343698204186575808495617", 10)
        self.v = v % self.modulus

    def __str__(self):
        return str(self.v)

    def add(self, f: 'Field') -> 'Field':
        return Field((self.v + f.v) % self.modulus)

    def mul(self, f: 'Field') -> 'Field':
        return Field((self.v * f.v) % self.modulus)

    def sub(self, f: 'Field') -> 'Field':
        return Field((self.v - f.v) % self.modulus)

    def neg(self) -> 'Field':
        return Field(-self.v % self.modulus)

    def div(self, f: 'Field') -> 'Field':
        return Field((self.v * f.inv().v) % self.modulus)

    def inv(self) -> 'Field':
        if self.v == 0:
            return self

        newt, t = 1, 0
        newr, r = self.v, self.modulus

        while newr != 0:
            q = r // newr
            t, newt = newt, t - q * newt
            r, newr = newr, r - q * newr

        return Field(t % self.modulus)