import sys
from argparse import Action
from datetime import datetime

from .db import DbClient
from .request import fetch_exchange_rates_by_currency
from currency_converter.config import get_config


class SetBaseCurrency(Action):
    def __init__(self, option_strings, dest, args=None, **kwargs):
        super().__init__(option_strings, dest, **kwargs)

    def __call__(self, parser, namespace, value, option_string=None):
        self.dest = value

        try:
            with DbClient('exchange_rates', 'config') as db:
                db.update(
                    {'base_currency': {'$ne': None}},
                    {'base_currency': value})

            print(f'Base currency set to {value}')
        except Exception as e:
            print(e)
        finally:
            sys.exit(0)


class UpdateForeignerExchangeRates(Action):
    def __init__(self, option_strings, dest, args=None, **kwargs):
        super().__init__(option_strings, dest, **kwargs)

    def __call__(self, parser, namespace, value, option_string=None):

        setattr(namespace, self.dest, True)

        try:
            config = get_config()
            base_currency = config['base_currency']
            print(('Fetching exchange rates from fixer.io'
                   f' [base currency: {base_currency}]'))
            response = fetch_exchange_rates_by_currency(base_currency)
            response['date'] = datetime.utcnow()

            with DbClient('exchange_rates', 'rates') as db:
                db.update(
                    {'base': base_currency},
                    response)
        except Exception as e:
            print(e)
        finally:
            sys.exit(0)
