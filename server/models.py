# coding: utf-8
# @2017
# Fauzi, fauziwei@yahoo.com
import sys
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
	'''The following only sample table will be created if not exist.'''
	__tablename__ = u'bike'
	__table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8', 'mysql_collate': 'utf8_general_ci'}
	id = Column('id', String(16), primary_key=True)


class Device(Base):
	'''The following only sample table will be created if not exist.'''
	__tablename__ = u'device'
	__table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8', 'mysql_collate': 'utf8_general_ci'}
	id = Column(u'id', String(16), primary_key=True)
	bike_id = Column(u'bike_id', String(16), ForeignKey('bike.id'), index=True)
	# work/test/maintain
	mode = Column(u'mode', Integer(), index=True)
	firmware = Column(u'firmware', Integer(), index=True)
	hardware = Column(u'hardware', Integer(), index=True)
	# longitude = Column(u'longitude', DOUBLE(), index=True)
	longitude = Column(u'longitude', Float(), index=True)
	# latitude = Column(u'latitude', DOUBLE(), index=True)
	latitude = Column(u'latitude', Float(), index=True)
	# gps data type
	gps_flags = Column(u'gps_flags', Integer(), index=True)
	# satellite number
	gps_satellite = Column(u'gps_satellite', Integer(), index=True)
	lock_status = Column(u'lock_status', Integer(), index=True)
	battery = Column(u'battery', Integer(), index=True)
	battery_percentage = Column(u'battery_percentage', Integer(), index=True)
	# charging status
	charging = Column(u'charging', Integer(), index=True)
	ble_key = Column(u'ble_key', String(16), index=True)
	# GSM signal strength
	csq = Column(u'csq', Integer(), index=True)
	# sim card ID
	sim = Column(u'sim', String(20), index=True)
	# phone number with sms
	phone = Column(u'phone', String(16), index=True)
	upgrade_flag = Column(u'upgrade_flag', Integer(), index=True)
	parameters = Column(u'parameters', String(12), index=True)
	scene = Column(u'scene', String(12), index=True)
	temp = Column(u'temp', Integer(), index=True) # ????
	vbus = Column(u'vbus', Integer(), index=True) # ???
	faults = Column(u'faults', Integer(), index=True)
	pedelec = Column(u'pedelec', Integer(), index=True)
	time = Column(u'time', DateTime(), index=True)

	bike = relationship(u'Bike', backref='devices')



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
	device.mode = 1
	device.firmware = 1
	device.hardware = 1
	device.longitude = 23.66666666
	device.latitude = 3.99999999
	device.gps_flags = 1
	device.gps_satellite = 1
	device.lock_status = 1
	device.battery = 1
	device.battery_percentage = 37
	device.charging = 1
	device.ble_key = '1234567812345678'
	device.csq = 1
	device.sim = '12345678123456781234'
	device.phone = '1234567812345678'
	device.upgrade_flag = 1
	device.parameters = '123456781234'
	device.scene = '123456781234'
	device.temp = 1
	device.vbus = 1
	device.faults = 0
	device.pedelec = 1
	device.time = datetime.datetime.now()
	session.add(device)
commit(session)
