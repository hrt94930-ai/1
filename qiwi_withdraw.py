import time
from datetime import datetime, timezone, timedelta
from typing import Union

import requests


class QiwiWithdraw:
    _token: str

    def __init__(self, token: str):
        self._token = token

    def transfer(self, number: str, transfer_sum: Union[float, int]):
        payment_id = int(datetime.now(timezone(timedelta(hours=3))).timestamp() * 1000)
        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {self._token}"
        }
        response = requests.post("https://edge.qiwi.com/sinap/api/v2/terms/99/payments", json={
            "id": str(payment_id),
            "sum": {
                "amount": transfer_sum,
                "currency": "643"
            },
            "paymentMethod": {
                "type": "Account",
                "accountId": "643"
            },
            "fields": {
                "account": number
            }
        }, headers=headers).json()
        if response.get("code") is not None:
            return False
        transaction_id = response['transaction']['id']
        time.sleep(0.5)
        transaction = requests.get(f"https://edge.qiwi.com/payment-history/v2/transactions/{transaction_id}",
                                   headers=headers).json()
        if transaction['status'] == "ERROR":
            return False
        return True
