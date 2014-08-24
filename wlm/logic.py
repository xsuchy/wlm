from wlm import db
from wlm import models
from datetime import datetime

import pygal

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
        db.session.add(sensor)
        db.session.commit()

    @classmethod
    def get_data(cls, sensor_id):
        rows = models.Measurement.query.filter_by(sensor_id=sensor_id).all()
        result1 = map(lambda x: x.depth, rows)
        result2 = map(lambda x: x.date, rows)
        return (result1, result2)
