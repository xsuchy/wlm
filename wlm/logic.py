# vim: expandtab:ts=4:sw=4
from wlm import db
from wlm import models
from collections import namedtuple
from datetime import datetime

import calendar
import pygal
import sqlalchemy

class SensorLogic(object):
    @classmethod
    def strip_macaddr(cls, macaddr):
        return macaddr.replace(':', '').lower()

    @classmethod
    def store_record(cls, macaddr, depth):
        macaddr = cls.strip_macaddr(macaddr)
        sensor = models.Sensor.query.filter_by(macaddr=macaddr).one()
        measurement = models.Measurement(
            sensor_id = sensor.id,
            depth = depth,
            date = datetime.utcnow(),
        )
        db.session.add(measurement)
        db.session.commit()

    @classmethod
    def get_data(cls, sensor_id):
        rows = models.Measurement.query.filter_by(sensor_id=sensor_id).all()
        result1 = map(lambda x: x.depth, rows)
        result2 = map(lambda x: x.date, rows)
        return (result1, result2)

    @classmethod
    def get_data_for_day(cls, sensor_id, year, month, day):
        query = 'SELECT depth, date_trunc(\'second\', date) AS "Time" FROM measurement WHERE sensor_id = :sensor_id AND (TIMESTAMP \'{year}-{month}-{day} 0:0:0\', TIMESTAMP \'{year}-{month}-{day} 24:0:0\') OVERLAPS (date, date) ORDER BY "Time"'.format(year=year+0, month=month+0, day=day+0)
        result = db.session.execute(query, {'sensor_id': sensor_id})
        Record = namedtuple('Record', result.keys())
        rows = [Record(*r) for r in result.fetchall()]
        result1 = map(lambda x: float(x.depth)/100 if x.depth is not None else None, rows)
        result2 = map(lambda x: x.Time, rows)
        return (result1, result2)

    @classmethod
    def get_data_for_month(cls, sensor_id, year, month):
        last_day = calendar.monthrange(year, month)[1]
        query = 'SELECT "Avg", "Hour" FROM (SELECT avg(depth) As "Avg", date_trunc(\'hour\', date) AS "Day" FROM measurement WHERE sensor_id = :sensor_id AND (DATE \'{year}-{month}-01\', DATE \'{year}-{month}-{last_day}\') OVERLAPS (date, date) GROUP BY "Day") AS "Data" RIGHT JOIN (SELECT generate_series( date\'{year}-{month}-01\' , date\'{year}-{month}-{last_day}\', \'1 hour\') as "Hour") AS "Hours" ON "Hours"."Hour" = "Data"."Day" ORDER BY "Hours"."Hour"'.format(year=year+0, month=month+0, last_day=last_day)
        result = db.session.execute(query, {'sensor_id': sensor_id})
        Record = namedtuple('Record', result.keys())
        rows = [Record(*r) for r in result.fetchall()]
        result1 = map(lambda x: float(x.Avg)/100 if x.Avg is not None else None, rows)
        result2 = map(lambda x: x.Hour, rows)
        return (result1, result2)
