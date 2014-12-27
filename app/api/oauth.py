import json
from datetime import datetime, timedelta
from flask import Blueprint
from flask import session, request, url_for
from flask import render_template, redirect, jsonify
from flask_oauthlib.provider import OAuth2Provider, OAuth2RequestValidator
from flask.ext.login import current_user
from werkzeug.security import gen_salt
from .. import config

from ..data.models import Client, Grant, Token, User
from ..data import mydb as db

oauth_blue = Blueprint( 'oauth_blue', __name__,template_folder='../templates')
oauth = OAuth2Provider()


@oauth.clientgetter
def load_client(client_id):
    return Client.query.filter_by(client_id=client_id).first()

@oauth.grantgetter
def load_grant(client_id, code):
    return Grant.query.filter_by(client_id=client_id, code=code).first()


@oauth.grantsetter
def save_grant(client_id, code, request, *args, **kwargs):
    # decide the expires time yourself
    expires = datetime.utcnow() + timedelta(seconds=100)
    grant = Grant(
        client_id=client_id,
        code=code['code'],
        redirect_uri=request.redirect_uri,
        _scopes=' '.join(request.scopes),
        user=current_user,
        expires=expires
    )
    db.session.add(grant)
    db.session.commit()
    return grant


@oauth.tokengetter
def load_token(access_token=None, refresh_token=None):
    if access_token:
        return Token.query.filter_by(access_token=access_token).first()
    elif refresh_token:
        return Token.query.filter_by(refresh_token=refresh_token).first()


@oauth.tokensetter
def save_token(token, request, *args, **kwargs):
    toks = Token.query.filter_by(
        client_id=request.client.client_id,
        user_id=request.user.id
    )
    # make sure that every client has only one token connected to a user
    for t in toks:
        db.session.delete(t)

    expires_in = token.pop('expires_in')
    expires = datetime.utcnow() + timedelta(seconds=expires_in)

    tok = Token(
        access_token=token['access_token'],
        refresh_token=token['refresh_token'],
        token_type=token['token_type'],
        _scopes=token['scope'],
        expires=expires,
        client_id=request.client.client_id,
        user_id=request.user.id,
    )
    db.session.add(tok)
    db.session.commit()
    return tok


@oauth_blue.route('/token')
@oauth.token_handler
def access_token():
    return None


def isOficialClient(client_id):
    if client_id in config.OFICIAL_CLIENTS_KEYS:
        return True
    return False

@oauth_blue.route('/authorize', methods=['GET', 'POST'])
@oauth.authorize_handler
def authorize(*args, **kwargs):
    user = current_user
    client_id = kwargs.get('client_id')
    response_type = kwargs.get('response_type')
    redirect_uri = kwargs.get('redirect_uri')
    data = {"response_type": response_type, "client_id": client_id, "redirect_uri": redirect_uri}
    if not user.is_authenticated():
       session['auth_args'] = json.dumps(data)
       return redirect(url_for('users.login'))
    if request.method == 'GET':
        oficial_client = isOficialClient(client_id)
        client = Client.query.filter_by(client_id=client_id).first()
        kwargs['client'] = client
        kwargs['user'] = user
        kwargs['oficial_client'] = oficial_client
        return render_template('authorize.html', **kwargs)
    confirm = request.form.get('confirm', 'no')
    return confirm == 'yes'

@oauth_blue.route('/clientgenerator')
def client():
    user = current_user
    if not user.is_authenticated():
        return redirect(url_for('users.login'))
    item = Client(
        client_id=gen_salt(40),
        client_secret=gen_salt(50),
        _redirect_uris=' '.join([
            'http://localhost:8000/authorized',
            'http://127.0.0.1:8000/authorized',
            'http://127.0.1:8000/authorized',
            'http://127.1:8000/authorized',
            ]),
        _default_scopes='email',
        user_id=user.id,
    )
    db.session.add(item)
    db.session.commit()
    return jsonify(
        client_id=item.client_id,
        client_secret=item.client_secret,
    )
