import os

import flask
from flask import request
from flask.ext.sqlalchemy import SQLAlchemy

app = flask.Flask(__name__)
app.config.from_pyfile("../config/wlm.conf", silent=False)
db = SQLAlchemy(app)

import wlm.models

@app.route('/')
def index():
    return flask.render_template('index.html', path=os.path.abspath(os.path.dirname(__file__)))

@app.route('/upload/', methods=['GET', 'PUT'])
def upload():
    data = request.args.get('data')
    rtc = request.args.get('rtc') # time
    mac = request.args.get('mac') # address
    #bss = request.args.get('bss') # access point address
    #bat = request.args.get('bat') # battery voltage
    #io = request.args.get('io') # GPIO in hex
    wake = request.args.get('wake') # wake reason
    seq = request.args.get('seq') # sequence value
    dev_id = request.args.get('id') # device id (to detect API capability)
    return flask.render_template('upload.html', path=os.path.abspath(os.path.dirname(__file__))), 200
    
