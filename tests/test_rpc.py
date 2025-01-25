import json

from zkwasm.rpc import ZKWasmAppRpc
import unittest

from zkwasm.sign import get_pid


class TestZKWasmAppRpc(unittest.TestCase):

    def setUp(self):
        self.rpc = ZKWasmAppRpc("http://localhost:3000")

    def get_nonce(self, prikey: str) -> int:
        state = self.rpc.query_state(prikey)
        data = json.loads(state["data"])
        return int(data["player"]["nonce"])

    def test_query_state(self):
        response = self.rpc.query_state(prikey="1234")
        print("state", response)

    def test_install_player(self):
        prikey = "1234"
        cmd = self.rpc.create_command(nonce=0, command=1,params=[])
        finished = self.rpc.send_transaction(cmd, prikey)
        print("init", finished)

    def test_buy_elf(self):
        prikey = "1234"
        nonce = self.get_nonce(prikey)
        print("nonce", nonce)
        ranch_id = 1
        elf_type = 1
        cmd = self.rpc.create_command(nonce=nonce, command=2, params=[ranch_id,elf_type])

        finished = self.rpc.send_transaction(cmd, prikey)
        print("finished", finished)


    def test_withdraw(self):
        prikey = "1234"
        nonce = self.get_nonce(prikey)
        print("nonce", nonce)
        address = "0xAE1e3fFA0A95b7c11CFD0A8f02d3250f20B51fF2"
        cmd = self.rpc.compose_withdraw_params(address=address,nonce=nonce, command=7, amount=1, token_index=0)
        finished = self.rpc.send_transaction(cmd, prikey)
        print("finished", finished)

    def test_query_config(self):
        response = self.rpc.query_config()
        print("config.py", response)

    def test_get_pid(self):
        prikey = "1234"
        pid = get_pid(prikey)
        print("pid", pid)


if __name__ == "__main__":
    unittest.main()
