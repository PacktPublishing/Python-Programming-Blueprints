import json
import sys
import argparse
from http import HTTPStatus

import requests


def setUpData(order_id):
    data = {
        "items": [
            {
                "name": "Prod 001",
                "price_per_unit": 10,
                "product_id": 1,
                "quantity": 2
            },
            {
                "name": "Prod 002",
                "price_per_unit": 12,
                "product_id": 2,
                "quantity": 2
            }
        ],
        "order_customer": {
            "customer_id": 14,
            "email": "test@test.com",
            "name": "Test User"
        },
        "order_id": order_id,
        "status": 1,
        "total": "190.00"
    }

    return data


def send_order(data):

    token = ''

    headers = {
        'Authorization': f'Token {token}',
        'Content-type': 'application/json'
    }

    response = requests.post(
        'http://127.0.0.1:8000/api/order/add/',
        headers=headers,
        data=json.dumps(data))

    if response.status_code == HTTPStatus.NO_CONTENT:
        print('Ops! Something went wrong!')
        sys.exit(1)

    print('Request was successfull')


if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description='Create a order for test')

    parser.add_argument('--orderid',
                        dest='order_id',
                        required=True,
                        help='Specify the the order id')

    args = parser.parse_args()

    data = setUpData(args.order_id)
    send_order(data)
