import requests
import json
import time

from .sign import query, sign


class ZKWasmAppRpc:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})

    def send_raw_transaction(self, cmd: list[int], prikey: str) -> dict:
        data = sign(cmd, prikey)
        response = self.session.post(f"{self.base_url}/send", json=data)
        if response.status_code == 201:
            return response.json()
        else:
            raise Exception("SendTransactionError")

    def send_transaction(self, cmd: list[int], prikey: str) -> dict:
        resp = self.send_raw_transaction(cmd, prikey)
        for _ in range(5):
            time.sleep(1)
            try:
                job_status = self.query_job_status(resp["jobid"])
                if "finishedOn" not in job_status:
                    raise Exception("WaitingForProcess")
            except Exception:
                continue
            if job_status:
                if "finishedOn" in job_status and "failedReason" not in job_status:
                    return job_status["returnvalue"]
                else:
                    raise Exception(job_status["failedReason"])
        raise Exception("MonitorTransactionFail")

    def query_state(self, prikey: str) -> dict:
        data = query(prikey)
        response = self.session.post(f"{self.base_url}/query", json=data)
        if response.status_code == 201:
            return response.json()
        else:
            raise Exception("UnexpectedResponseStatus")

    def query_config(self) -> dict:
        response = self.session.post(f"{self.base_url}/config")
        if response.status_code == 201:
            return response.json()
        else:
            raise Exception("QueryConfigError")

    def query_job_status(self, job_id: int) -> dict:
        response = self.session.get(f"{self.base_url}/job/{job_id}")
        if response.status_code == 201:
            return response.json()
        else:
            raise Exception("QueryJobError")

    def get_nonce(self, prikey: str) -> int:
        state = self.query_state(prikey)
        data = json.loads(state["data"])
        return int(data["player"]["nonce"])
