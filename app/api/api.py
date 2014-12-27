import json
from flask import Blueprint
from flask import session, request, url_for
from flask import render_template, redirect, jsonify
from ..data.models import *
from ..data import mydb as db
from .. import config

from flask.ext.login import current_user

from .oauth import oauth, oauth_blue
#from flask.ext.httpauth import HTTPBasicAuth

import requests

#auth_basic = HTTPBasicAuth()
api = Blueprint( 'api', __name__,template_folder='../templates')

def register_apis(app, url_prefix="/api"):
    app.register_blueprint(oauth_blue, url_prefix='/oauth')
    app.register_blueprint(api, url_prefix=url_prefix)

#@api.route('/login')
#@auth_basic.login_required
#def login():
#    pass

#@auth_basic.verify_password
#def verify_password(username, password):
#    user = User.query.filter_by(username = username).first()
#    if not user or not user.is_valid_password(password):
#        return False
#    #g.user = user
#    return True


@api.route('/me')
@oauth.require_oauth()
def me():
    user = request.oauth.user
    return jsonify(username=user.username)


@api.route('/users',  methods=['GET'])
def getUsers():
    user =  User.query.first_or_404()
    return jsonify(user.toDict())


@api.route('/echo', methods = ['GET', 'POST', 'PATCH', 'PUT', 'DELETE'])
def api_echo():
    if request.method == 'GET':
        return "ECHO: GET\n"

    elif request.method == 'POST':
        return "ECHO: POST\n"

    elif request.method == 'PATCH':
        return "ECHO: PACTH\n"

    elif request.method == 'PUT':
        return "ECHO: PUT\n"

    elif request.method == 'DELETE':
        return "ECHO: DELETE"

