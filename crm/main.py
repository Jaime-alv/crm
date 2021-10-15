import sys
import re
import json
import pathlib
import flask
from flask import Flask

app = Flask(__name__)


@app.route('/', methods=['GET'])
def index():
    return app.send_static_file('index.html')


@app.route('/login')
def login():
    return app.send_static_file('login.html')


@app.route('/sign_up')
def sign_up():
    return app.send_static_file('sign_up.html')


@app.route('/sign_up_form', methods=['POST'])
def sign_up_form():
    missing_field = []
    fields = ['organization', 'email', 'password', 'password_confirm']

    # check if all fields are complete -> form validation
    for field in fields:
        value = flask.request.form.get(field)
        if value == '':
            missing_field.append(field)
    if missing_field:
        return error(f'Missing inputs in {missing_field}', 'sign_up')

    # check if email is already registered
    new_user = flask.request.form.get('email')
    organization = flask.request.form.get('organization')
    if pathlib.Path(f'..\\user\\{organization}\\{new_user}').exists():
        return error('User already exits', 'sign_up')

    # check if email is valid
    email_regex = re.compile(r"[a-zA-Z0-9_.]+@[a-zA-Z0-9_.+]+")
    email = email_regex.search(new_user)
    if email is None:
        return error('email is not valid', 'sign_up')

    # check if password is valid
    password = flask.request.form.get('password')
    password_confirm = flask.request.form.get('password_confirm')
    if (any(character.islower() for character in password)
            and any(character.isupper() for character in password)
            and any(character.isdigit() for character in password)
            and password == password_confirm):
        create_new_user(organization, new_user, password)
        return flask.render_template('profile.html')
    else:
        return error('Password needs at least 1 upper, 1 digit and 1 punctuation', 'index')


# create user folder and json file with all data
def create_new_user(organization, email, password):
    if not pathlib.Path(f'..\\user\\{organization}').exists():
        pathlib.Path(f'..\\user\\{organization}').mkdir(exist_ok=True)
    data = {'organization': organization,
            'user': email,
            'password': password,
            'messages': {},
            'friends': [],
            }
    with pathlib.Path(f'..\\user\\{organization}\\{email}.txt').open('w') as f:
        json.dump(data, f)


# generic error message, redirect to 'next_url'
def error(message, next_url):
    return flask.render_template('error.html', error_message=message, next=flask.url_for(next_url))


if __name__ == '__main__':
    if sys.platform == 'darwin':  # different port if running on MacOsX
        app.run(debug=True, port=8080)
    else:
        app.run(debug=True, port=80)
