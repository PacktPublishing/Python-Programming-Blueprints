from argparse import ArgumentParser

from .app_logger import get_logger


def validated_args(args):
    logger = get_logger()

    unique_hashtags = list(set(args.hashtags))

    if len(unique_hashtags) < len(args.hashtags):
        logger.info(('Some hashtags passed as arguments were '
                     'duplicated and are going to be ignored'))

        args.hashtags = unique_hashtags

    if len(args.hashtags) > 4:
        logger.error('Voting app accepts only 4 hashtags at the time')
        args.hashtags = args.hashtags[:4]

    return args


def parse_commandline_args():
    argparser = ArgumentParser(
        prog='twittervoting',
        description='Collect votes using twitter hashtags.')

    required = argparser.add_argument_group('require arguments')

    required.add_argument(
        '-ht', '--hashtags',
        nargs='+',
        required=True,
        dest='hashtags',
        help=('Space separated list specifying the '
              'hashtags that will be used for the voting.\n'
              'Type the hashtags without the hash symbol.'))

    args = argparser.parse_args()

    return validated_args(args)
