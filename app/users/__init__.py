import json
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask.ext.login import LoginManager, UserMixin, current_user, login_user, logout_user
from flask.ext.login import login_required

from .forms import LoginForm, RegistrationForm
from ..data.models import User
from ..data import mydb as db

from flask import session, request, url_for

users = Blueprint('users', __name__)
controller = users

login_manager = LoginManager()

@login_manager.user_loader
def user_loader(user_id):
    """Given *user_id*, return the associated User object.

    :param unicode user_id: user_id (email) user to retrieve
    """
    return User.query.get(user_id)

@login_manager.unauthorized_handler
def unauthorized_callback():
	return redirect('/login')
    #return redirect('/login?next=' + request.path)

@controller.route('/login/', methods=('GET', 'POST'))
def login():
    form = LoginForm()
    if form.validate_on_submit():
        login_user(form.user)
        flash("Logged in successfully.")
        if 'auth_args' in session: 
            auth_args = json.loads(session.get('auth_args'))
            session.pop('auth_args', None)
            return redirect(url_for('oauth_blue.authorize', response_type = str(auth_args['response_type']), client_id = str(auth_args['client_id']), redirect_uri = str(auth_args['redirect_uri'])))
        # There's a subtle security hole in this code, which we will be fixing in our next article.
        # Don't use this exact pattern in anything important.
        return redirect(request.args.get("next") or "/")
    return render_template('users/login.html', form=form,  current_user=current_user)


@controller.route('/register/', methods=('GET', 'POST'))
def register():
    user = current_user
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(**form.data)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect('/')
    return render_template('users/register.html', form=form, current_user=user)


@controller.route('/logout/')
def logout():
    logout_user()
    return redirect('/')
