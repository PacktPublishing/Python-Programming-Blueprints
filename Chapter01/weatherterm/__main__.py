import sys
from argparse import ArgumentParser
from weatherterm.core import parser_loader
from weatherterm.core import ForecastType
from weatherterm.core import Unit

from weatherterm.core import SetUnitAction


def _validate_forecast_args(args):
    if args.forecast_option is None:
        err_msg = ('One of these arguments must be used: '
                   '-td/--today, -5d/--fivedays, -10d/--tendays, -w/--weekend')

        print(f'{argparser.prog}: error: {err_msg}', file=sys.stderr)
        sys.exit()

parsers = parser_loader.load('./weatherterm/parsers')

argparser = ArgumentParser(
    prog='weatherterm',
    description='Weather info from weather.com on your terminal')

required = argparser.add_argument_group('require arguments')
required.add_argument('-p', '--parser',
    choices=parsers.keys(),
    required=True,
    dest='parser',
    help=('Specify which parser is going to be used to '
           'scrape weather information.'))

unit_values = [name.title() for name, value in Unit.__members__.items()]

argparser.add_argument('-u', '--unit',
    choices=unit_values,
    required=False,
    action=SetUnitAction,
    dest='unit',
    help=('Specify the unit that will be used to display '
    'the temperatures.'))

required.add_argument('-a', '--areacode',
    required=True,
    dest='area_code',
    help=('The code area to get the weather broadcast from .'
          'It can be obtained at https: // weather.com'))

argparser.add_argument('-v', '--version',
    action='version',
    version='%(prog)s 1.0')

argparser.add_argument('-td', '--today',
    dest='forecast_option',
    action='store_const',
    const=ForecastType.TODAY,
    help='Show the weather forecast for the current day')

argparser.add_argument('-5d', '--fivedays',
                       dest='forecast_option',
                       action='store_const',
                       const=ForecastType.FIVEDAYS,
                       help='Shows the weather forecast for the next 5 days')

argparser.add_argument('-10d', '--tendays',
                       dest='forecast_option',
                       action='store_const',
                       const=ForecastType.TENDAYS,
                       help='Shows the weather forecast for the next 10 days')

argparser.add_argument('-w', '--weekend',
                       dest='forecast_option',
                       action='store_const',
                       const=ForecastType.WEEKEND,
                       help=('Shows the weather forecast for the next or '
                             'current weekend'))

args = argparser.parse_args()
_validate_forecast_args(args)

cls = parsers[args.parser]
parser = cls()
results = parser.run(args)

for result in results:
    print(result)