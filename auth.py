import os
from flask import current_app, g
from authlib.flask.client import OAuth

import app

def setup():
    # Initializing OAuth
    oauth = OAuth(current_app)
    current_app.secret_key = os.environ['APP_SECRET']

    global auth0
    auth0 = oauth.register(
    'auth0',
    client_id=os.environ['AUTH0_CLIENT_ID'],
    client_secret=os.environ['AUTH0_CLIENT_SECRET'],
    api_base_url='https://' + os.environ['AUTH0_DOMAIN'],
    access_token_url='https://' + os.environ['AUTH0_DOMAIN']+'/oauth/token',
    authorize_url='https://' + os.environ['AUTH0_DOMAIN']+'/authorize',
    client_kwargs={
        'scope': 'openid profile',
    },
)