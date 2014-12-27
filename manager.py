from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand
from app import app
from app import config
from app.data.models import *
from app.data import mydb as db
import os

#app.config.from_object(os.environ['APP_SETTINGS'])
app.config.from_object(config)

migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()
