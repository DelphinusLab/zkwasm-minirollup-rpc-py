from .Field import Field
from .config import config


def pow5(a: Field) -> Field:
    return a.mul(a.mul(a.mul(a.mul(a))))


def sbox_full(state: list[Field]) -> list[Field]:
    for i in range(len(state)):
        tmp = state[i].mul(state[i])
        state[i] = state[i].mul(tmp)
        state[i] = state[i].mul(tmp)
    return state


def add_constants(a: list[Field], b: list[Field]) -> list[Field]:
    return [v.add(b[i]) for i, v in enumerate(a)]


def apply(matrix: list[list[Field]], vector: list[Field]) -> list[Field]:
    result = [Field(0)] * len(matrix)
    for i in range(len(matrix)):
        for j in range(len(matrix[i])):
            result[i] = result[i].add(matrix[i][j].mul(vector[j]))
    return result


def apply_sparse_matrix(matrix: dict, state: list[Field]) -> list[Field]:
    words = [Field(value.v) for value in state]
    state0 = Field(0)

    for i in range(len(words)):
        f = Field(int(matrix['row'][i], 16))
        state0 = state0.add(f.mul(words[i]))

    state[0] = state0
    for i in range(1, len(words)):
        hat = Field(int(matrix['col_hat'][i - 1], 16))
        state[i] = hat.mul(words[0]).add(words[i])

    return state


def trim_hex(s: str) -> str:
    return s[2:] if s.startswith('0x') else s


def to_field_array(arr: list[str]) -> list[Field]:
    return [Field(int(trim_hex(value), 16)) for value in arr]


def to_field_matrix(arr: list[list[str]]) -> list[list[Field]]:
    return [to_field_array(row) for row in arr]


class Poseidon:
    def __init__(self, config):
        self.config = config
        self.state = [Field(0)] * self.config['t']
        self.state[0] = Field(int('0000000000000000000000000000000000000000000000010000000000000000', 16))
        self.absorbing = []
        self.squeezed = False

    def get_state(self) -> list[Field]:
        return self.state

    def permute(self):
        rf = self.config['r_f'] // 2

        # First half of full rounds
        self.state = add_constants(self.state, to_field_array(self.config['constants']['start'][0]))
        for i in range(1, rf):
            self.state = sbox_full(self.state)
            self.state = add_constants(self.state, to_field_array(self.config['constants']['start'][i]))
            self.state = apply(to_field_matrix(self.config['mds_matrices']['mds']), self.state)

        self.state = sbox_full(self.state)
        self.state = add_constants(self.state, to_field_array(self.config['constants']['start'][-1]))
        self.state = apply(to_field_matrix(self.config['mds_matrices']['pre_sparse_mds']), self.state)

        # Partial rounds
        for i in range(min(len(self.config['constants']['partial']),
                           len(self.config['mds_matrices']['sparse_matrices']))):
            self.state[0] = pow5(self.state[0])
            self.state[0] = self.state[0].add(Field(int(trim_hex(self.config['constants']['partial'][i]), 16)))
            apply_sparse_matrix(self.config['mds_matrices']['sparse_matrices'][i], self.state)

        # Second half of full rounds
        for constants in self.config['constants']['end']:
            self.state = sbox_full(self.state)
            self.state = add_constants(self.state, to_field_array(constants))
            self.state = apply(to_field_matrix(self.config['mds_matrices']['mds']), self.state)

        self.state = sbox_full(self.state)
        self.state = apply(to_field_matrix(self.config['mds_matrices']['mds']), self.state)

    def update_exact(self, elements: list[Field]) -> Field:
        if self.squeezed:
            raise Exception("Cannot update after squeeze")
        if len(elements) != self.config['rate']:
            raise Exception(f"Invalid input size: {len(elements)}")

        for j in range(self.config['rate']):
            self.state[j + 1] = self.state[j + 1].add(elements[j])

        self.permute()
        return self.state[1]

    def update(self, elements: list[Field]):
        if self.squeezed:
            raise Exception("Cannot update after squeeze")

        for i in range(0, len(elements), self.config['rate']):
            if i + self.config['rate'] > len(elements):
                self.absorbing = elements[i:]
            else:
                chunk = elements[i:i + self.config['rate']]
                for j in range(self.config['rate']):
                    self.state[j + 1] = self.state[j + 1].add(chunk[j])
                self.permute()
                self.absorbing = []

    def squeeze(self) -> Field:
        last_chunk = self.absorbing
        last_chunk.append(Field(1))

        for i in range(min(len(last_chunk), len(self.state) - 1)):
            self.state[i + 1] = self.state[i + 1].add(last_chunk[i])

        self.permute()
        self.absorbing = []
        return self.state[1]


def poseidon(inputs: list[Field]) -> Field:
    if not inputs:
        raise Exception(f"Invalid input size: {len(inputs)}")

    hasher = Poseidon(config)
    hasher.update(inputs)
    return hasher.squeeze()