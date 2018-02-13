import sys

from .core.cmdline_parser import parse_commandline_args
from .config import get_config
from .core import DbClient
from .core import fetch_exchange_rates_by_currency


def main():
    args = parse_commandline_args()
    value = args.value
    dest_currency = args.dest_currency
    from_currency = args.from_currency

    config = get_config()
    base_currency = (from_currency
                     if from_currency
                     else config['base_currency'])

    with DbClient('exchange_rates', 'rates') as db:
        exchange_rates = db.find_one({'base': base_currency})

        if exchange_rates is None:
            print(('Fetching exchange rates from fixer.io'
                   f' [base currency: {base_currency}]'))

            try:
                response = fetch_exchange_rates_by_currency(base_currency)
            except Exception as e:
                sys.exit(f'Error: {e}')

            dest_rate = response['rates'][dest_currency]
            db.update({'base': base_currency}, response)
        else:
            dest_rate = exchange_rates['rates'][dest_currency]

        total = round(dest_rate * value, 2)
        print(f'{value} {base_currency} = {total} {dest_currency}')


if __name__ == '__main__':
    main()
