from zkwasm.rpc import ZKWasmAppRpc
import unittest

from zkwasm.sign import  get_pid


class TestZKWasmAppRpc(unittest.TestCase):

    def create_command(self, nonce: int, command: int, objindex: int) -> int:
        return (nonce << 16) + (objindex << 8) + command

    def setUp(self):
        self.rpc = ZKWasmAppRpc("https://zk-server.pumpelf.ai")

    def get_nonce(self, prikey: str) -> int:
        state = self.rpc.query_state(prikey)
        print("state", state)
        return state["data"]["player"]["nonce"]

    def test_query_state(self):
        response = self.rpc.query_state(prikey="1234")
        print("state", response)

    def test_install_player(self):
        prikey = "1234"
        cmd = [self.create_command(nonce=0, command=1, objindex=0), 0, 0, 0]
        finished = self.rpc.send_transaction(cmd, prikey)
        print("init", finished)

    def test_buy_elf(self):
        prikey = "1234"
        nonce = self.get_nonce(prikey)
        ranch_id = 1
        elf_type = 1
        cmd = [
            self.create_command(nonce=nonce, command=2, objindex=0),
            ranch_id,
            elf_type,
            0,
        ]
        finished = self.rpc.send_transaction(cmd, prikey)
        print("finished", finished)

    def test_query_config(self):
        response = self.rpc.query_config()
        print("config", response)

    def test_get_pid(self):
        prikey = "1234"
        pid = get_pid(prikey)
        print("pid", pid)


if __name__ == "__main__":
    unittest.main()
