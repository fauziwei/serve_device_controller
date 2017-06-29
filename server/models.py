# coding: utf-8
# @2017
# Fauzi, fauziwei@yahoo.com
import sys
import uuid
import datetime
import traceback
from sqlalchemy import String, Integer, Float, DateTime, \
	Column, Table, ForeignKey, MetaData, create_engine
from sqlalchemy.dialects.mysql import DOUBLE
from sqlalchemy.orm  import sessionmaker, relationship
from sqlalchemy.pool import NullPool
from sqlalchemy.ext.declarative import declarative_base

reload(sys)
sys.setdefaultencoding('utf-8')

# ---------------------------------------------------
# The following sample for MySQL,
# Change the longitude and latitude to DOUBLE in class Device
# address = '127.0.0.1'
# port = 3306
# user = 'your_user'
# password = 'your_password'
# database = 'your_database'

# engine = create_engine('mysql+pymysql://%s:%s@%s:%s/%s?charset=utf8' %
# 	(user, password, address, port, database), encoding='utf8', poolclass=NullPool, echo=False)

# ---------------------------------------------------
# The following sample for SQLite
engine = create_engine('sqlite:///sqlite.db', encoding='utf8', poolclass=NullPool, echo=False)
# ---------------------------------------------------

metadata = MetaData(engine)
Base = declarative_base(metadata=metadata)

class Db(object):
	'''Session creator.'''

	def __init__(self):
		self.Session = sessionmaker()
		self.Session.configure(bind=engine)

	@property
	def session(self):
		return self.Session()

def commit(session):
	try:
		session.flush()
		session.commit()
	except:
		traceback.print_exc()
		session.rollback()
	finally:
		session.close()


# ---------------------------------------------------
# The models is started from here...

class Bike(Base):
	__tablename__ = u'bike'
	__table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8', 'mysql_collate': 'utf8_general_ci'}
	id = Column('id', String(16), primary_key=True)


class Device(Base):
	__tablename__ = u'device'
	__table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8', 'mysql_collate': 'utf8_general_ci'}
	id = Column(u'id', String(16), primary_key=True)
	bike_id = Column(u'bike_id', String(16), ForeignKey('bike.id'), index=True)
	sim = Column(u'sim', String(20), index=True)
	phone = Column(u'phone', String(16), index=True)
	ble_key = Column(u'ble_key', String(16), index=True)
	parameter = Column(u'parameter', String(12), index=True)
	firmware = Column(u'firmware', Integer(), index=True)
	hardware = Column(u'hardware', Integer(), index=True)
	temp = Column(u'temp', Integer(), index=True)
	vbus = Column(u'vbus', Integer(), index=True)
	vbattery = Column(u'vbattery', Integer(), index=True)
	upgrade_flag = Column(u'upgrade_flag', Integer(), index=True)
	scene = Column(u'scene', String(12), index=True)
	fault = Column(u'fault', Integer(), index=True)
	pedelec = Column(u'pedelec', Integer(), index=True)

	bike = relationship(u'Bike', backref='devices')


class Status(Base):
	__tablename__ = u'status'
	__table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8', 'mysql_collate': 'utf8_general_ci'}
	id = Column(u'id', String(36), primary_key=True)
	device_id = Column(u'device_id', String(16), ForeignKey('device.id'), index=True)
	longitude = Column(u'longitude', Float(), index=True)
	# longitude = Column(u'longitude', DOUBLE(), index=True)
	latitude = Column(u'latitude', Float(), index=True)
	# latitude = Column(u'latitude', DOUBLE(), index=True)
	lock_status = Column(u'lock_status', Integer(), index=True)
	csq = Column(u'csq', Integer(), index=True) # GSM Signal Strength
	gps_flags = Column(u'gps_flags', Integer(), index=True) # GPS Type
	gps_satellite = Column(u'gps_satellite', Integer(), index=True) # Sat Number
	battery_percent = Column(u'battery_percent', Integer(), index=True)
	battery_charging = Column(u'battery_charging', Integer(), index=True)
	mode = Column(u'mode', Integer(), index=True)
	start_count = Column(u'start_count', DateTime(), index=True)
	last_used = Column(u'last_used', DateTime(), index=True)

	device = relationship(u'Device', backref='statuses')



# Auto create if doesnt exist.
Base.metadata.create_all(engine)


# Sample record.

# Create bike
session = Db().Session()
bike_id = '1234567812345678'
bike = session.query(Bike).filter_by(id=bike_id).first()
if not bike:
	bike = Bike()
	bike.id = bike_id
	session.add(bike)
commit(session)

# Create device
session = Db().Session()
device_id = '2469040358b6e392'
device = session.query(Device).filter_by(id=device_id).first()
if not device:
	device = Device()
	device.id = device_id
	device.bike_id = bike_id
	device.sim = '12345678123456781234'
	device.phone = '1234567812345678'
	device.ble_key = '1234567812345678'
	device.parameter = '123456781234'
	device.firmware = 1
	device.hardware = 1
	device.temp = 1
	device.vbus = 1
	device.vbattery = 1
	device.upgrade_flag = 1
	device.scene = '123456781234'
	device.fault = 0
	device.pedelec = 1
	session.add(device)
commit(session)

# Create status
session = Db().Session()
status = session.query(Status).filter_by(device_id=device_id).first()
if not status:
	status = Status()
	status.id = str(uuid.uuid4())
	status.device_id = device_id
	status.longitude = 23.66666666
	status.latitude = 3.99999999
	status.lock_status = 1
	status.csq = 1
	status.gps_flags = 1
	status.gps_satellite = 1
	status.battery_percent = 37
	status.battery_charging = 1
	status.mode = 1
	status.start_count = datetime.datetime.now()
	status.last_used = datetime.datetime.now()
	session.add(status)
commit(session)
