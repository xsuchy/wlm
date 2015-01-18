# vim: expandtab:ts=4:sw=4
#from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

from wlm import db

class Measurement(db.Model):
    __tablename__ = 'measurement'
    id = db.Column(db.Integer, primary_key=True)
    sensor_id = db.Column(db.Integer, db.ForeignKey("sensor.id", onupdate="CASCADE", ondelete="CASCADE"))
    # depth is in centimeters
    depth = db.Column(db.Integer)
    date = db.Column(db.DateTime)

    def __repr__(self):
        return 'Sensor {0} on {1}: {2}'.format(self.sensor, self.date, self.depth)

class Sensor(db.Model):
    __tablename__ = 'sensor'
    id = db.Column(db.Integer, primary_key=True)
    macaddr = db.Column(db.String(12), index=True)
    # calibration: low is 0m in V, high is 50m in V
    cal_low = db.Column(db.Float(3))
    cal_high = db.Column(db.Float(3))
    owner_id = db.Column(db.Integer, db.ForeignKey("user.id", onupdate="CASCADE", ondelete="CASCADE"))
    measurement = db.relationship("Measurement", backref=db.backref("sensor"))

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, index=True)
    password = db.Column('password' , db.String(80))
    email = db.Column(db.String(120), unique=True, index=True)
    sensor = db.relationship("Sensor", backref=db.backref("owner"))

    def __init__(self, username, password, email):
        self.username = username
        self.email = email
        self.password = password

    def __repr__(self):
        return '<User {0}>'.format(self.username)

    def is_authenticated(self):
        return True
 
    def is_active(self):
        return True
 
    def is_anonymous(self):
        return False
 
    def get_id(self):
        return str(self.id)
