# coding: utf-8
from flask import Flask
from flask import session, request, url_for
from flask import render_template, redirect, jsonify
from flask.ext.login import current_user
from flask import make_response
import re

from data import mydb as db
from api.api import oauth, register_apis
import config
from data.models import *
import logging

from users  import controller as users, login_manager 

app = Flask(__name__, template_folder='templates')
app.config.from_object(config)

#app.config['SQLALCHEMY_ECHO'] = True

# add the flask log handlers to sqlalchemy
loggers = [logging.getLogger('sqlalchemy.engine'),
logging.getLogger('flask_oauthlib')]
for logger in loggers:
    for handler in app.logger.handlers:
        logger.addHandler(handler)

#register extensions
db.init_app(app)
oauth.init_app(app)
login_manager.init_app(app)

#register apis
register_apis(app)

#register blueprints
app.register_blueprint(users)
	
@app.route('/')
def home():
    user = current_user
    return render_template('home.html', user=user)

@app.errorhandler(404)
def not_found(error):
    if re.match("/api/*", request.path):
	return make_response(jsonify({'error': 'Not found'}), 404)
    return make_response('Not found', 404)
