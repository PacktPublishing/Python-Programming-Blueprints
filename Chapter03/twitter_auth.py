from urllib.parse import parse_qsl

import yaml

from flask import Flask
from flask import render_template
from flask import request

import oauth2 as oauth

from core import read_config
from core.models import RequestToken


app = Flask(__name__)

client = None
consumer = None
req_token = None


def get_oauth_token(config):

    global consumer
    global client
    global req_token

    consumer = oauth.Consumer(config.consumer_key, config.consumer_secret)
    client = oauth.Client(consumer)

    resp, content = client.request(config.request_token_url, 'GET')

    if resp['status'] != '200':
        raise Exception("Invalid response {}".format(resp['status']))

    request_token = dict(parse_qsl(content.decode('utf-8')))

    req_token = RequestToken(**request_token)


@app.route('/')
def home():
    config = read_config()

    get_oauth_token(config)

    url = f'{config.authorize_url}?oauth_token={req_token.oauth_token}'

    return render_template('index.html', link=url)


@app.route('/callback')
def callback():

    global req_token
    global consumer

    config = read_config()

    oauth_verifier = request.args.get('oauth_verifier', '')

    token = oauth.Token(req_token.oauth_token,
                        req_token.oauth_token_secret)

    token.set_verifier(oauth_verifier)

    client = oauth.Client(consumer, token)

    resp, content = client.request(config.access_token_url, 'POST')
    access_token = dict(parse_qsl(content.decode('utf-8')))

    with open('.twitterauth', 'w') as req_auth:
        file_content = yaml.dump(access_token, default_flow_style=False)
        req_auth.write(file_content)

    return 'All set! You can close the browser window and stop the server.'


if __name__ == '__main__':
    app.run(host='localhost', port=3000)
