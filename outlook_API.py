"""Flask-OAuthlib sample for Microsoft Graph"""
# Copyright (c) Microsoft. All rights reserved. Licensed under the MIT license.
# See LICENSE in the project root for license information.
import os
import uuid
from time import time

import flask
import requests_oauthlib

import config

from openTimeSlots import findOpenTimeSlots

APP = flask.Flask(__name__, template_folder='static/templates')
APP.debug = True
APP.secret_key = 'development'
# OAUTH = OAuth(APP)

# Enable non-HTTPS redirect URI for development/testing.
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
# Allow token scope to not match requested scope. (Other auth libraries allow
# this, but Requests-OAuthlib raises exception on scope mismatch by default.)
os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'
os.environ['OAUTHLIB_IGNORE_SCOPE_CHANGE'] = '1'

refresh_url = config.AUTHORITY_URL + config.TOKEN_ENDPOINT

MSGRAPH = requests_oauthlib.OAuth2Session(config.CLIENT_ID,
                                          scope=config.SCOPES,
                                          redirect_uri=config.REDIRECT_URI)
# MSGRAPH = OAUTH.remote_app(
#     'microsoft', consumer_key=config.CLIENT_ID, consumer_secret=config.CLIENT_SECRET,
#     request_token_params={'scope': config.SCOPES},
#     base_url=config.RESOURCE + config.API_VERSION + '/',
#     request_token_url=None, access_token_method='POST',
#     access_token_url=config.AUTHORITY_URL + config.TOKEN_ENDPOINT,
#     authorize_url=config.AUTHORITY_URL + config.AUTH_ENDPOINT)

@APP.route('/')
def homepage():
    """Render the home page."""
    return flask.render_template('homepage.html', sample='Flask-OAuthlib')

@APP.route('/login')
def login():
    """Prompt user to authenticate."""
    flask.session['state'] = str(uuid.uuid4())
    if 'state' in flask.session:
        state = flask.session['state']
        print('state PRINT HERE: ', flask.session['state'])

    auth_base = config.AUTHORITY_URL + config.AUTH_ENDPOINT
    authorization_url, state = MSGRAPH.authorization_url(auth_base,
                                                         access_type = "offline")
    flask.session['state'] = state
    # print('state PRINT HERE 2: ', flask.session['state'])

    return flask.redirect(authorization_url)

@APP.route('/login/authorized')
def authorized():
    """Handler for the application's Redirect Uri."""
    #print('state PRINT HERE 3: ', flask.session['state'])
    if str(flask.session['state']) != str(flask.request.args['state']):
        raise Exception('state returned to redirect URL does not match!')

    token = MSGRAPH.fetch_token(config.AUTHORITY_URL + config.TOKEN_ENDPOINT,
                                client_secret=config.CLIENT_SECRET,
                                authorization_response=flask.request.url)
    flask.session['access_token'] = token
    return flask.redirect('/graphcall')

@APP.route('/graphcall')
def graphcall():
    if 'access_token' in flask.session:
        token = flask.session['access_token']
    else:
        raise Exception('no session of access_token in graphcall module')
    """Confirm user authentication by calling Graph and displaying some data."""

    #ISO 8601 format yyyy-mm-ddTHH:MM:SS.miliseconds
    #call these values from a config.py file
    startTime = '2018-09-15T06:00:00.0000000'
    endTime =   '2018-09-15T18:00:00.0000000'

    endpoint = config.RESOURCE + config.API_VERSION + '/me/calendar/calendarView?startDateTime={}&endDateTime={}'.format(startTime,endTime)
    headers = {'Authentication': 'Bearer {}'.format(token),
                'Prefer': 'outlook.timezone = "Eastern Standard Time"'
                }
    graphdata = MSGRAPH.get(endpoint, headers=headers).json()

    #list [{event1},{event2}]
    events = graphdata.get('value', [])
    dict1 = {}
    dict1 = findOpenTimeSlots(events)
    return flask.jsonify(dict1)

# #have to integrate refresh token somehow 
# @APP.route('/auto_refreshToken')
# def auto_refreshToken():
#     if 'access_token' in flask.session:
#         token = flask.session['access_token']
#     else:
#         raise Exception('no session of access_token in refreshToken module')
    
#     token['expires_at'] = time() - 10
#     extra = { 
#             'client_id': config.CLIENT_ID,
#             'clienet_secret':config.CLIENT_SECRET
#     }

#     def token_updater(token):
#         flask.session['access_token'] = token

#     MSGRAPH = requests_oauthlib.OAuth2Session(config.CLIENT_ID,
#                                             token=token,
#                                             auto_refresh_kwargs=extra,
#                                             auto_refresh_url=refresh_url,
#                                             token_updater=token_updater)

#     # flask.session['access_token'] = MSGRAPH.token
#     # bug check: 
#     if str(flask.session['access_token']) != str(MSGRAPH.token):
#          raise Exception('tokens do not match')

#     endpoint = config.RESOURCE + config.API_VERSION + '/me/calendar/events'
#     headers = {'Authentication': 'Bearer {}'.format(MSGRAPH.token)
#                 }

#     graphdata = MSGRAPH.get(endpoint, headers=headers).json()



if __name__ == '__main__':
    APP.run()