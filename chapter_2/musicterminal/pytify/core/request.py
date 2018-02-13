import requests
import json

from .exceptions import BadRequestError
from .config import read_config
from .request_type import RequestType


def execute_request(
        url_template,
        auth,
        params,
        request_type=RequestType.GET,
        payload=()):

    conf = read_config()

    params['base_url'] = conf.base_url

    url = url_template.format(**params)

    headers = {
        'Authorization': f'Bearer {auth.access_token}'
    }

    if request_type is RequestType.GET:
        response = requests.get(url, headers=headers)
    else:
        response = requests.put(url, headers=headers, data=json.dumps(payload))

        if not response.text:
            return response.text

    result = json.loads(response.text)

    if not response.ok:
        error = result['error']
        raise BadRequestError(
            f'{error["message"]} (HTTP {error["status"]})')

    return result