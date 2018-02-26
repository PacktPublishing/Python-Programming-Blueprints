from urllib.parse import urlencode


def validate_params(params, required=None):

    if required is None:
        return

    partial = {x: x in params.keys() for x in required}
    not_supplied = [x for x in partial.keys() if not partial[x]]

    if not_supplied:
        msg = f'The parameter(s) `{", ".join(not_supplied)}` are required'
        raise AttributeError(msg)


def prepare_params(params, required=None):

    if params is None and required is not None:
        msg = f'The parameter(s) `{", ".join(required)}` are required'
        raise ValueError(msg)
    elif params is None and required is None:
        return ''
    else:
        validate_params(params, required)

    query = urlencode(
        '&'.join([f'{key}={value}' for key, value in params.values()])
    )

    return f'?{query}'
