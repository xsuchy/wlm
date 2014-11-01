# vim: expandtab:ts=4:sw=4

import os
import pygal
import flask
import sqlalchemy
from flask import request, Response
from flask.ext.sqlalchemy import SQLAlchemy

app = flask.Flask(__name__)
app.config.from_pyfile("/etc/wlm/wlm.conf", silent=False)
app.config.from_pyfile("../config/wlm.conf", silent=True)
db = SQLAlchemy(app)

import wlm.models
from wlm.logic import SensorLogic

@app.route('/')
def index():
    return flask.render_template('index.html', path=os.path.abspath(os.path.dirname(__file__)))

@app.route('/login/')
def login():
    if flask.g.user is not None:
        return flask.redirect(oid.get_next_url())
    else:
        return oid.try_login("https://id.fedoraproject.org/",
                             ask_for=["email", "timezone"])

@app.route('/oauth2callback')
def oauth2callback()
    raise

@app.route('/upload/', methods=['GET', 'PUT'])
def upload():
    data = request.args.get('data')
    rtc = request.args.get('rtc') # time (or rather uptime)
    mac = request.args.get('mac') # address
    #bss = request.args.get('bss') # access point address
    #bat = request.args.get('bat') # battery voltage
    #io = request.args.get('io') # GPIO in hex
    #wake = request.args.get('wake') # wake reason (1 == power on or hw reset)
    seq = request.args.get('seq') # sequence value (reset on each reboot of device)
    dev_id = request.args.get('id') # device id (to detect API capability)

    if (dev_id == "wlm-v1"):
        sensors_raw_data = [data[i:i+4] for i in range(0, len(data), 4)]
        # 0 is gpio, 1 is ch.0, 2 is ch.1...etc. we care about ch.5
        analog_hexa = sensors_raw_data[6]
        analog_int = int(analog_hexa, 16)
        # data in micro Volts, samplings is by 24 micro Volts
        analog_uV = analog_int * 24
        # 400 000 is max, which is 50 m
        # / 80 to get to meter = value 100 is one meter so value is in cm
        depth = analog_uV / 80 # now in cm, in int not float
        try:
            SensorLogic.store_record(mac, depth)
            return flask.render_template('upload.html', path=os.path.abspath(os.path.dirname(__file__))), 200
        except sqlalchemy.orm.exc.NoResultFound as e:
            return flask.render_template("404.html"), 404
    else:
        return flask.render_template("404.html"), 404

@app.route('/render/', methods=['GET'])
def render():
    #mac = request.args.get('mac')
    render_type = request.args.get('type')
    sensor_id = 1
    line_chart = pygal.Line(show_legend=False)
    line_chart.title = 'Depth (in cm)'
    if render_type == 'month':
        year_month = request.args.get('year_month')
    (depths, dates) = SensorLogic.get_data(sensor_id)
    line_chart.x_labels = map(str, dates)
    line_chart.add(None, depths)
    return Response(line_chart.render(), mimetype='image/svg+xml')
