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
    def get_data_for_month(cls, sensor_id, year, month):
        last_day = calendar.monthrange(year, month)[1]
        query = 'SELECT min(depth) AS "Min", max(depth) AS "Max", EXTRACT(DAY FROM date) AS "Day" FROM measurement WHERE (DATE \'{year}-{month}-01\', DATE \'{year}-{month}-{last_day}\') OVERLAPS (date, date) GROUP BY "Day" ORDER BY "Day"'.format(year=year+0, month=month+0, last_day=last_day)
        result = db.session.execute(query)
        Record = namedtuple('Record', result.keys())
        rows = [Record(*r) for r in result.fetchall()]
        result1 = map(lambda x: x.Min, rows)
        result2 = map(lambda x: x.Max, rows)
        result3 = map(lambda x: x.Day, rows)
        return (result1, result2, result3)
