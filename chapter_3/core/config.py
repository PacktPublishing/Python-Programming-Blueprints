import os
import yaml

from .models import Config
from .models import RequestAuth


def _read_yaml_file(filename, cls):
    core_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(core_dir, '..', filename)

    with open(file_path, mode='r', encoding='UTF-8') as file:
        config = yaml.load(file)
        return cls(**config)


def read_config():
    try:
        return _read_yaml_file('config.yaml', Config)
    except IOError as e:
        print(""" Error: couldn\'t file the configuration file `config.yaml`
        'on your current directory.

        Default format is:',

        consumer_key: 'your_consumer_key'
        consumer_secret: 'your_consumer_secret'
        request_token_url: 'https://api.twitter.com/oauth/request_token'
        access_token_url: 'https://api.twitter.com/oauth/access_token'
        authorize_url: 'https://api.twitter.com/oauth/authorize'
        api_version: '1.1'
        search_endpoint: ''
        """)
        raise


def read_reqauth():
    try:
        return _read_yaml_file('.twitterauth', RequestAuth)
    except IOError as e:
        print(('It seems like you have not authorized the application.\n'
               'In order to use your twitter data, please run the '
               'auth.py first.'))
