# vim: expandtab:ts=4:sw=4
import calendar
import os
import hashlib
import pygal
import requests
import flask
import sqlalchemy
import sys
from flask import request, Response, render_template
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager, login_required, login_required, \
    logout_user, login_user
from datetime import datetime
from flask import session

app = flask.Flask(__name__)
app.config.from_pyfile("/etc/wlm/wlm.conf", silent=False)
app.config.from_pyfile("../config/wlm.conf", silent=True)
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

import wlm.models
from wlm.logic import SensorLogic

@login_manager.user_loader
def load_user(userid):
    """ Loads user from session """
    try:
        return models.User.query.filter_by(id=int(userid)).one()
    except sqlalchemy.orm.exc.NoResultFound:
        return None

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    password = hashlib.sha1(request.form['password'].encode('utf-8')).hexdigest()
    user = wlm.models.User(request.form['username'] , password, request.form['email'])
    db.session.add(user)
    try:
        db.session.commit()
    except:
        flask.flash('User already exist.')
        return flask.redirect(flask.url_for('register'))
    flask.flash('User successfully registered')
    return flask.redirect(flask.url_for('login'))
 
@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    username = request.form['username']
    password = hashlib.sha1(request.form['password'].encode('utf-8')).hexdigest()
    registered_user = wlm.models.User.query.filter_by(username=username,password=password).first()
    if registered_user is None:
        flask.flash('Username or Password is invalid' , 'error')
        return flask.redirect(flask.url_for('login'))
    flask.ext.login.login_user(registered_user)
    flask.flash('Logged in successfully')
    return flask.redirect(request.args.get('next') or flask.url_for('dashboard'))

@app.route("/logout")
@login_required
def logout():
    flask.ext.login.logout_user()
    return flask.redirect("/")

@app.route('/')
def index():
    return flask.render_template('index.html', path=os.path.abspath(os.path.dirname(__file__)))

@app.route('/dashboard/')
@login_required
def dashboard():
    return render_template("dashboard.html")

@app.route('/oauth2callback')
def oauth2callback():
    if 'error' in request.args or 'code' not in request.args:
        return flask.redirect('/loginfailed/')

    access_token_uri = 'https://accounts.google.com/o/oauth2/token'
    redirect_uri = "http://mysite/login/google/auth"
    params = urllib.urlencode({
        'code':request.args.get['code'],
        'redirect_uri':redirect_uri,
        'client_id': flask.current_app.config['CLIENT_ID'],
        'client_secret': flask.current_app.config['CLIENT_SECRET'],
        'grant_type':'authorization_code'
    })
    headers={'content-type':'application/x-www-form-urlencoded'}
    r = requests.post(access_token_uri, data = params, headers = headers)
    token_data = r.json()
    r = requests.get("https://www.googleapis.com/oauth2/v1/userinfo?access_token={accessToken}".format(accessToken=token_data['access_token']))
    #this gets the google profile!!
    google_profile = r.json()
    sys.stderr.write(google_profile)
    #log the user in-->
    #HERE YOU LOG THE USER IN, OR ANYTHING ELSE YOU WANT
    #THEN REDIRECT TO PROTECTED PAGE
    return flask.redirect('/')


@app.route('/upload/', methods=['GET', 'PUT'])
def upload():
    data = request.args.get('data')
    rtc = request.args.get('rtc') # time (or rather uptime)
    mac = request.args.get('mac') # MAC address of rn-171
    #bss = request.args.get('bss') # access point MAC
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

@app.route('/render/all/', methods=['GET'])
def render_all():
    #mac = request.args.get('mac')
    render_type = request.args.get('type')
    sensor_id = 1
    line_chart = pygal.Line(show_legend=False)
    line_chart.title = 'Depth (metres)'
    (depths, dates) = (None, None)
    if render_type == 'month':
        year_month = request.args.get('year_month')
        (depths, dates) = SensorLogic.get_data(sensor_id)
    else:
        (depths, dates) = SensorLogic.get_data(sensor_id)
    line_chart.x_labels = map(str, dates)
    line_chart.add(None, depths)
    return Response(line_chart.render(), mimetype='image/svg+xml')


@app.route('/render/year-month/', defaults={"year": None, "month": None})
@app.route('/render/year-month/<int:year>/<int:month>/', methods=['GET'])
def render_year_month(year, month):
    #mac = request.args.get('mac')
    sensor_id = 1
    line_chart = pygal.Line(show_legend=False, y_title='metres',
        x_labels_major_every=24, show_minor_x_labels=False,
        human_readable=True, dots_size=1,
        show_x_guides=True, style=pygal.style.LightenStyle('#0284c4'),
        tooltip_border_radius=10, print_zeroes=True, no_prefix=True, print_values=False,
        #this is very slow on client
        #interpolate='hermite', interpolation_parameters={'type': 'cardinal', 'c': .75}
        )
    line_chart.value_formatter = lambda x: "%.2f" % x
    if year is None:
       year = datetime.now().year
    if month is None:
       month = datetime.now().month
    line_chart.title = 'Water level for {0}/{1}'.format(month, year)
    (depths, dates) = SensorLogic.get_data_for_month(sensor_id, year, month)
    #line_chart.x_labels = map(lambda x: str(x).split(' ')[0], dates)
    line_chart.x_labels = []
    last_day = calendar.monthrange(year, month)[1]
    for i in range(1, last_day+1):
        line_chart.x_labels.append(str(i))
        line_chart.x_labels.extend(['']*23)
    line_chart.add(None, depths)
    return Response(line_chart.render(), mimetype='image/svg+xml')

@app.route('/render/day/', defaults={"year": None, "month": None, "day": None})
@app.route('/render/day/<int:year>/<int:month>/<int:day>/', methods=['GET'])
def render_day(year, month, day):
    #mac = request.args.get('mac')
    sensor_id = 1
    line_chart = pygal.Line(show_legend=False, y_title='metres',
        x_labels_major_every=60, show_minor_x_labels=False,
        human_readable=True, dots_size=1,
        show_x_guides=True, style=pygal.style.LightenStyle('#0284c4'),
        #interpolate='hermite', interpolation_parameters={'type': 'cardinal', 'c': .75}
        )
    line_chart.value_formatter = lambda x: "%.2f" % x
    if year is None:
       year = datetime.now().year
    if month is None:
       month = datetime.now().month
    if day is None:
       day = datetime.now().day
    line_chart.title = 'Water level for {0}-{1}-{2}'.format(year, month, day)
    (depths, dates) = SensorLogic.get_data_for_day(sensor_id, year, month, day)
    #line_chart.x_labels = map(str, dates)
    line_chart.x_labels = []
    for i in range(0, 24):
        line_chart.x_labels.append(str(i))
        line_chart.x_labels.extend(['']*59)
    line_chart.x_labels.append('24')
    line_chart.add(None, depths)
    return Response(line_chart.render(), mimetype='image/svg+xml')
