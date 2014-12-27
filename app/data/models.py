from . import mydb as db
from . import DictMapper, mapper, as_dict
from datetime import datetime as date_time


from sqlalchemy.ext.hybrid import hybrid_property
from hashlib import sha512
#from backports.pbkdf2 import pbkdf2_hmac, compare_digest

from random import SystemRandom
from flask.ext.login import UserMixin

class User(UserMixin, db.Model, DictMapper):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(40), unique=True)
    name = db.Column(db.String(50))
    email = db.Column(db.String(120), unique=True)
    contry_id = db.Column(db.ForeignKey('contry.id'))
    contry = db.relationship('Contry')
    _password = db.Column(db.String(128))
    _salt = db.Column(db.String(128))

    @hybrid_property
    def password(self):
        return self._password

    # In order to ensure that passwords are always stored
    # hashed and salted in our database we use a descriptor
    # here which will automatically hash our password
    # when we provide it (i. e. user.password = "12345")
    @password.setter
    def password(self, value):
        # When a user is first created, give them a salt
        if self._salt is None:
            self._salt = bytes(SystemRandom().getrandbits(128))
        self._password = self._hash_password(value)

    def is_valid_password(self, password):
        """Ensure that the provided password is valid.

        We are using this instead of a ``sqlalchemy.types.TypeDecorator``
        (which would let us write ``User.password == password`` and have the incoming
        ``password`` be automatically hashed in a SQLAlchemy query)
        because ``compare_digest`` properly compares **all***
        the characters of the hash even when they do not match in order to
        avoid timing oracle side-channel attacks."""
        new_hash = self._hash_password(password)
        #return compare_digest(new_hash, self._password)
        return new_hash == self._password

    def _hash_password(self, password):
        #pwd = password.encode("utf-8")
        #salt = bytes(self._salt)
        #rounds = 100000
        #buff = pbkdf2_hmac("sha512", pwd, salt, iterations=rounds)
        #return bytes(buff)
        pwhash = sha512(password + self._salt)
        return pwhash.hexdigest()

    def __repr__(self):
        return "<User #{:d}>".format(self.id)
        
    @mapper(exclude=['password','contry_id'])		
    def toDict(self):
        pass


class Client(db.Model):
    client_id = db.Column(db.String(40), primary_key=True)
    #client_name = db.Column(db.String(40))
    client_secret = db.Column(db.String(55), nullable=False)

    user_id = db.Column(db.ForeignKey('user.id'))
    user = db.relationship('User')

    _redirect_uris = db.Column(db.Text)
    _default_scopes = db.Column(db.Text)

    @property
    def client_type(self):
        return 'public'

    @property
    def redirect_uris(self):
        if self._redirect_uris:
            return self._redirect_uris.split()
        return []

    @property
    def default_redirect_uri(self):
        return self.redirect_uris[0]

    @property
    def default_scopes(self):
        if self._default_scopes:
            return self._default_scopes.split()
        return []


class Grant(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer, db.ForeignKey('user.id', ondelete='CASCADE')
    )
    user = db.relationship('User')

    client_id = db.Column(
        db.String(40), db.ForeignKey('client.client_id'),
        nullable=False,
    )
    client = db.relationship('Client')

    code = db.Column(db.String(255), index=True, nullable=False)

    redirect_uri = db.Column(db.String(255))
    expires = db.Column(db.DateTime)

    _scopes = db.Column(db.Text)

    def delete(self):
        db.session.delete(self)
        db.session.commit()
        return self

    @property
    def scopes(self):
        if self._scopes:
            return self._scopes.split()
        return []


class Token(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(
        db.String(40), db.ForeignKey('client.client_id'),
        nullable=False,
    )
    client = db.relationship('Client')

    user_id = db.Column(
        db.Integer, db.ForeignKey('user.id')
    )
    user = db.relationship('User')

    # currently only bearer is supported
    token_type = db.Column(db.String(40))

    access_token = db.Column(db.String(255), unique=True)
    refresh_token = db.Column(db.String(255), unique=True)
    expires = db.Column(db.DateTime)
    _scopes = db.Column(db.Text)

    @property
    def scopes(self):
        if self._scopes:
            return self._scopes.split()
        return []


class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(55), nullable=False)
    description = db.Column(db.String(140), nullable=False)
    long_description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    location = db.Column(db.String(40))
    create_date = db.Column(db.DateTime, default=date_time.utcnow)
    update_date = db.Column(db.DateTime, onupdate=date_time.utcnow)
    user_id = db.Column(db.ForeignKey('user.id'))
    user = db.relationship('User')


class Contry(db.Model, DictMapper):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(55), nullable=False)
    default_currency_id = db.Column(db.ForeignKey('currency.id'))
    default_currency = db.relationship('Currency')
    @mapper(exclude=["default_currency", "default_currency_id"])		
    def toDict(self):
        pass
    
class Currency(db.Model, DictMapper):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(55), nullable=False)
    symbol = db.Column(db.String(5), nullable=False)
    abbr = db.Column(db.String(5), nullable=False)
    
