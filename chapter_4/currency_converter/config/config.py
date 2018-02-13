from .config_error import ConfigError
from currency_converter.core import DbClient


def get_config():
    config = None

    with DbClient('exchange_rates', 'config') as db:
        config = db.find_one()

    if config is None:
        error_message = ('It was not possible to get your base currency, that '
                         'probably happened because it have not been '
                         'set yet.\n Please, use the option '
                         '--setbasecurrency')
        raise ConfigError(error_message)

    return config
