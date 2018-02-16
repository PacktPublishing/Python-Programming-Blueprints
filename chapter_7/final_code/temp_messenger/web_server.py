import yaml

from flask.views import MethodView
from nameko.standalone.rpc import ClusterRpcProxy
from flask.json import jsonify
from nameko.exceptions import RemoteError

from flask import (
    Flask,
    render_template,
    request,
    session,
    redirect,
    url_for,
)

with open('config.yaml', 'r') as config_file:
    config = yaml.load(config_file)

app = Flask(__name__)
app.secret_key = config['FLASK_SECRET_KEY']


@app.route('/')
def home():
    authenticated = user_authenticated()
    return render_template(
        'home.html', authenticated=authenticated
    )


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))


class MessageAPI(MethodView):

    def get(self):
        with ClusterRpcProxy(config) as rpc:
            messages = rpc.message_service.get_all_messages()

        return jsonify(messages)

    def post(self):
        if not user_authenticated():
            return 'Please log in', 401

        email = session['email']
        data = request.get_json(force=True)

        try:
            message = data['message']
        except KeyError:
            return 'No message given', 400

        with ClusterRpcProxy(config) as rpc:
            rpc.message_service.save_message(email, message)

        return '', 204


class LoginView(MethodView):

    def get(self):
        if user_authenticated():
            return redirect(url_for('home'))
        else:
            return render_template('login.html')

    def post(self):
        email = request.form['email']
        password = request.form['password']

        with ClusterRpcProxy(config) as cluster_rpc:
            try:
                cluster_rpc.user_service.authenticate_user(
                    email=email,
                    password=password,
                )
            except RemoteError as err:
                app.logger.error(
                    'Bad login for %s - %s', email, str(err)
                )
                return render_template(
                    'login.html', login_error=True
                )

        session['authenticated'] = True
        session['email'] = email

        return redirect(url_for('home'))


class SignUpView(MethodView):

    def get(self):
        if user_authenticated():
            return redirect(url_for('home'))
        else:
            return render_template('sign_up.html')

    def post(self):
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        password = request.form['password']

        with ClusterRpcProxy(config) as cluster_rpc:
            try:
                cluster_rpc.user_service.create_user(
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    password=password,
                )
            except RemoteError as err:
                message = 'Unable to create user - {}'.format(
                    err.value
                )
                app.logger.error(message)
                return render_template(
                    'sign_up.html', error_message=message
                )

        session['authenticated'] = True
        session['email'] = email

        return redirect(url_for('home'))


def user_authenticated():
    return session.get('authenticated', False)


app.add_url_rule(
    '/messages', view_func=MessageAPI.as_view('messages')
)
app.add_url_rule(
    '/sign_up', view_func=SignUpView.as_view('sign_up')
)
app.add_url_rule(
    '/login', view_func=LoginView.as_view('login')
)
