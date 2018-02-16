import requests
import json

from order import settings

from .notification_type import NotificationType


def notify(order, notification_type):
    endpoint = ('notify/order-received/'
                if notification_type is NotificationType.ORDER_RECEIVED
                else 'notify/order-shipped/')

    header = {
        'X-API-Key': settings.NOTIFIER_API_KEY
    }

    response = requests.post(
        f'{settings.NOTIFIER_BASEURL}/{endpoint}',
        json.dumps(order.data),
        headers=header
    )

    return response