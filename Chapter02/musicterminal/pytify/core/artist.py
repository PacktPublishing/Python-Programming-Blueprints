from .parameter import prepare_params
from .request import execute_request


def get_artist_albums(artist_id, auth, params=None):

    if artist_id is None or artist_id is "":
        raise AttributeError(
            'Parameter `artist_id` cannot be `None` or empty.')

    url_template = '{base_url}/{area}/{artistid}/{postfix}{query}'
    url_params = {
        'query': prepare_params(params),
        'area': 'artists',
        'artistid': artist_id,
        'postfix': 'albums',
        }

    return execute_request(url_template, auth, url_params)