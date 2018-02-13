import sys
from argparse import ArgumentParser

from .actions import UpdateForeignerExchangeRates
from .actions import SetBaseCurrency
from .currency import Currency


def validate_args(args):

    fields = [arg for arg in vars(args).items() if arg]

    if not fields:
        return False

    if args.value and not args.dest_currency:
        return False
    elif args.dest_currency and not args.value:
        return False

    return True


def parse_commandline_args():

    currency_options = [currency.name for currency in Currency]

    argparser = ArgumentParser(
        prog='currency_converter',
        description=('Tool that shows exchange rated and perform '
                     'currency convertion, using http://fixer.io data.'))

    argparser.add_argument('--setbasecurrency',
                           type=str,
                           dest='base_currency',
                           choices=currency_options,
                           action=SetBaseCurrency,
                           help='Sets the base currency to be used.')

    argparser.add_argument('--update',
                           metavar='',
                           dest='update',
                           nargs=0,
                           action=UpdateForeignerExchangeRates,
                           help=('Update the foreigner exchange rates '
                                 'using as a reference the base currency'))

    argparser.add_argument('--basecurrency',
                           type=str,
                           dest='from_currency',
                           choices=currency_options,
                           help=('The base currency. If specified it will '
                                 'override the default currency set by'
                                 'the --setbasecurrency option'))

    argparser.add_argument('--value',
                           type=float,
                           dest='value',
                           help='The value to be converted')

    argparser.add_argument('--to',
                           type=str,
                           dest='dest_currency',
                           choices=currency_options,
                           help=('Specify the currency that the value will '
                                 'be converted to.'))

    args = argparser.parse_args()

    if not validate_args(args):
        argparser.print_help()
        sys.exit()

    return args
