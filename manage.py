#!/usr/bin/env python

import os

import flask
from flask.ext.script import Manager, Command, Option

from wlm import app
from wlm import db, models


class CreateDBCommand(Command):
    'Create DB and tables.'
    def run(self, alembic_ini=None):
        if flask.current_app.config['SQLALCHEMY_DATABASE_URI'].startswith('sqlite'):
            # strip sqlite:///
            datadir_name = os.path.dirname(
                flask.current_app.config['SQLALCHEMY_DATABASE_URI'][len('sqlite:///'):])
            if not os.path.exists(datadir_name):
                os.makedirs(datadir_name)
        db.create_all()
        # load the Alembic configuration and generate the
        # version table, "stamping" it with the most recent rev:
        from alembic.config import Config
        from alembic import command
        alembic_cfg = Config(alembic_ini)
        command.stamp(alembic_cfg, "head")

    option_list = (
        Option("--alembic",
               "-f",
               dest="alembic_ini",
               help="Path to the alembic configuration file (alembic.ini)",
               required=True),
    )

class DropDBCommand(Command):
    'Drop DB tables.'
    def run(self):
        db.drop_all()

class CreateUserCommand(Command):
    'Create an user.'
    def run(self, username):
        user = models.User(
            username = username
        )
        db.session.add(user)
        db.session.commit()

    option_list = (
        Option("username",
               help="Login of the user."),
    )

class CreateSensorCommand(Command):
    'Create a sensor.'
    def run(self, username, macaddr):
        macaddr = macaddr.replace(':', '').lower()
        if len(macaddr) != 12:
            sys.stderr.write('Error: Malformed MAC address\n')
        user = models.User.query.filter_by(username=username).one()
        sensor = models.Sensor(
            macaddr = macaddr,
            owner = user
        )
        db.session.add(sensor)
        db.session.commit()

    option_list = (
        Option("username",
               help="Login of the user."),
        Option("macaddr",
               help="MAC address of sensor."),
    )

manager = Manager(app)
manager.add_command('create_db', CreateDBCommand())
manager.add_command('drop_db', DropDBCommand())
manager.add_command('create_user', CreateUserCommand())
manager.add_command('create_sensor', CreateSensorCommand())

if __name__ == '__main__':
    manager.run()
