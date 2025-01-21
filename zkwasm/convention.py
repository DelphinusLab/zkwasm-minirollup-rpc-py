import hashlib
import os
from web3 import Web3
from decimal import Decimal
import json


def bytes_to_hex(bytes):
    return "".join(f"{byte:02x}" for byte in bytes)


def bytes_to_decimal(bytes):
    return "".join(f"{byte:02d}" for byte in bytes)


def compose_withdraw_params(address, amount):
    address_be = address.to_bytes(20, byteorder="big")
    first_limb = int.from_bytes(address_be[:4][::-1], byteorder="big")
    snd_limb = int.from_bytes(address_be[4:12][::-1], byteorder="big")
    third_limb = int.from_bytes(address_be[12:20][::-1], byteorder="big")
    return [(first_limb << 32) + amount, snd_limb, third_limb]


def decode_withdraw(txdata):
    r = []
    if len(txdata) > 1:
        for i in range(0, len(txdata), 32):
            extra = txdata[i : i + 4]
            address = txdata[i + 4 : i + 24]
            amount = txdata[i + 24 : i + 32]
            amount_in_wei = Decimal(bytes_to_decimal(list(amount)))
            r.append(
                {
                    "op": extra[0],
                    "index": extra[1],
                    "address": Web3.to_checksum_address(bytes_to_hex(list(address))),
                    "amount": amount_in_wei,
                }
            )
    return r


class PlayerConvention:
    def __init__(self, key, rpc, command_deposit, command_withdraw):
        self.processing_key = key
        self.rpc = rpc
        self.command_deposit = command_deposit
        self.command_withdraw = command_withdraw

    def create_command(self, nonce, command, objindex):
        return (nonce << 16) + (objindex << 8) + command

    async def get_config(self):
        config = await self.rpc.query_config()
        return config

    async def get_state(self):
        state = await self.rpc.query_state(self.processing_key)
        parsed_state = json.loads(json.dumps(state))
        data = json.loads(parsed_state["data"])
        return data

    async def get_nonce(self):
        data = await self.get_state()
        nonce = int(data["player"]["nonce"])
        return nonce

    async def deposit(self, pid_1, pid_2, amount):
        nonce = await self.get_nonce()
        try:
            state = await self.rpc.send_transaction(
                [
                    self.create_command(nonce, self.command_deposit, 0),
                    pid_1,
                    pid_2,
                    amount,
                ],
                self.processing_key,
            )
            return state
        except Exception as e:
            raise e

    async def withdraw_rewards(self, address, amount):
        nonce = await self.get_nonce()
        address_int = int(address, 16)
        a = address_int.to_bytes(20, byteorder="big")

        first_limb = int.from_bytes(a[:4][::-1], byteorder="big")
        snd_limb = int.from_bytes(a[4:12][::-1], byteorder="big")
        third_limb = int.from_bytes(a[12:20][::-1], byteorder="big")

        try:
            state = await self.rpc.send_transaction(
                [
                    self.create_command(nonce, self.command_withdraw, 0),
                    (first_limb << 32) + amount,
                    snd_limb,
                    third_limb,
                ],
                self.processing_key,
            )
            return state
        except Exception as e:
            raise e
