from collections import namedtuple


Authorization = namedtuple('Authorization', [
    'access_token',
    'token_type',
    'expires_in',
    'scope',
    'refresh_token',
])