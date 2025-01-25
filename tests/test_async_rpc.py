import json
import unittest

from zkwasm.rpc import AsyncZKWasmAppRpc


class TestAsyncZKWasmAppRpc(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        self.rpc = AsyncZKWasmAppRpc("http://localhost:3000")
        
    async def get_nonce(self, prikey: str) -> int:
        state = await self.rpc.query_state(prikey)
        data = json.loads(state["data"])
        return int(data["player"]["nonce"])

    async def test_query_state(self):
        response = await self.rpc.query_state(prikey="12345")
        print("state", response)

    async def test_install_player(self):
        prikey = "12345"
        cmd = await self.rpc.create_command(nonce=0, command=1, params=[])
        finished = await self.rpc.send_transaction(cmd, prikey)
        print("init", finished)

    async def test_buy_elf(self):
        prikey = "12345"
        nonce = await self.get_nonce(prikey)
        print("nonce", nonce)
        ranch_id = 1
        elf_type = 1
        cmd = await self.rpc.create_command(nonce=nonce, command=2, params=[ranch_id, elf_type])

        finished = await self.rpc.send_transaction(cmd, prikey)
        print("finished", finished)

    async def test_withdraw(self):
        prikey = "12345"
        nonce = await self.get_nonce(prikey)
        print("nonce", nonce)
        address = "0xAE1e3fFA0A95b7c11CFD0A8f02d3250f20B51fF2"
        cmd = await self.rpc.compose_withdraw_params(address=address, nonce=nonce, command=7, amount=1, token_index=0)
        finished = await self.rpc.send_transaction(cmd, prikey)
        print("finished", finished)

    async def test_query_config(self):
        response = await self.rpc.query_config()
        print("config.py", response)

    async def test_get_pid(self):
        prikey = "12345"
        pid = await self.rpc.get_pid(prikey)
        print("pid", pid)


if __name__ == "__main__":
    unittest.main() 