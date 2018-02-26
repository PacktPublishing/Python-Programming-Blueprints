from collections import namedtuple

Config = namedtuple('Config', ['consumer_key',
                               'consumer_secret',
                               'request_token_url',
                               'access_token_url',
                               'authorize_url',
                               'api_version',
                               'search_endpoint', ])


RequestToken = namedtuple('RequestToken', ['oauth_token',
                                           'oauth_token_secret',
                                           'oauth_callback_confirmed'])


RequestAuth = namedtuple('RequestAuth', ['oauth_token',
                                         'oauth_token_secret',
                                         'user_id',
                                         'screen_name',
                                         'x_auth_expires', ])
