import os
import pygal
import flask
from flask import request, Response
from flask.ext.sqlalchemy import SQLAlchemy

app = flask.Flask(__name__)
app.config.from_pyfile("../config/wlm.conf", silent=False)
db = SQLAlchemy(app)

import wlm.models
from wlm.logic import SensorLogic

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


@app.route('/render/', methods=['GET'])
def render():
    #mac = request.args.get('mac')
    sensor_id = 1
    line_chart = pygal.Line(show_legend=False)
    line_chart.title = 'Depth (in cm)'
    (depths, dates) = SensorLogic.get_data(sensor_id)
    line_chart.x_labels = map(str, dates)
    line_chart.add(None, depths)
    return Response(line_chart.render(), mimetype='image/svg+xml')
