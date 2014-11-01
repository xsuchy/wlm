# vim: expandtab:ts=4:sw=4
from wlm import db
from wlm import models
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
    def get_data_for_month(cls, sensor_id, year_month):
        year, month = year_month.split(-)
        last_day = calendar.monthrange(year, month)
        rows = models.Measurement.query.filter_by(sensor_id=sensor_id).filter(models.Measurement.date.between("{0}-01".format(year_month), "{0}-{1}".format(year_month, last_day)))\
		.group_by(sqlalchemy.func.day(models.Measurement.date)).all()
        result1 = map(lambda x: x.depth, rows)
        result2 = map(lambda x: x.date, rows)
        return (result1, result2)
