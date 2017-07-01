# coding: utf-8
# @2017
# Fauzi, fauziwei@yahoo.com
import sys
import uuid
import hashlib
import datetime
import traceback
from sqlalchemy import SmallInteger, Integer, BigInteger, \
	Float, String, Boolean, DateTime, \
	Column, Table, ForeignKey, MetaData, create_engine
from sqlalchemy.dialects.mysql import DOUBLE, TINYINT
from sqlalchemy.orm  import sessionmaker, relationship
from sqlalchemy.pool import NullPool
from sqlalchemy.ext.declarative import declarative_base

reload(sys)
sys.setdefaultencoding('utf-8')

# ---------------------------------------------------
# Development.
# SQLite
engine = create_engine('sqlite:///sqlite.db', encoding='utf8', poolclass=NullPool, echo=False)

# ---------------------------------------------------
# Production.
# MySQL
# address = '127.0.0.1'
# port = 3306
# user = 'your_user'
# password = 'your_password'
# database = 'your_database'
# engine = create_engine('mysql+pymysql://%s:%s@%s:%s/%s?charset=utf8' %
# 	(user, password, address, port, database), encoding='utf8', poolclass=NullPool, echo=False)


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
# --------------------------------------------------

# Oauth2 models.

class Client(Base):
	'''Client application.'''
	__tablename__ = u'client'
	__table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8', 'mysql_collate': 'utf8_general_ci'}
	id = Column('id', String(36), primary_key=True) # uuid4
	secret = Column('secret', String(36), index=True, nullable=False) # uuid4


class User(Base):
	'''User controller.'''
	__tablename__ = u'user'
	__table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8', 'mysql_collate': 'utf8_general_ci'}
	id = Column('id', String(36), primary_key=True) # uuid4
	email = Column('email', String(150), index=True, nullable=False)
	salt = Column('salt', String(36), index=True, nullable=False) # uuid4
	password = Column('password', String(32), index=True, nullable=False) # md5


# --------------------------------------------------
# CLASS STATUS
# Development.
class Status(Base):
	'''One device to one record.'''
	__tablename__ = u'status'
	__table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8', 'mysql_collate': 'utf8_general_ci'}
	bike_id = Column(u'bike_id', BigInteger(), primary_key=True)
	device_id = Column(u'device_id', BigInteger(), index=True)
	firmware = Column(u'firmware', SmallInteger(), index=True)
	hardware = Column(u'hardware', SmallInteger(), index=True)
	temp = Column(u'temp', Integer(), index=True)
	longitude = Column(u'longitude', Float(), index=True)
	latitude = Column(u'latitude', Float(), index=True)
	address = Column(u'address', String(150))
	gps_type = Column(u'gps_type', Integer(), index=True)
	lock_status = Column(u'lock_status', Integer(), index=True)
	battery_percent = Column(u'battery_percent', Integer(), index=True)
	mode = Column(u'mode', Integer(), index=True)
	abnormal = Column(u'abnormal', Integer(), index=True)
	faults = Column(u'faults', Integer(), index=True)
	timestamp = Column(u'timestamp', Integer(), index=True)
	ble_key = Column(u'ble_key', String(16), index=True)
	upgrade_flag = Column(u'upgrade_flag', Integer(), index=True)
	update_time = Column(u'update_time', DateTime(), index=True)
	active = Column(u'active', Boolean(), index=True)

# Production.
# class Status(Base):
# 	'''One device to one record.'''
# 	__tablename__ = u'status'
# 	__table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8', 'mysql_collate': 'utf8_general_ci'}
# 	bike_id = Column(u'bike_id', BigInteger(), primary_key=True)
# 	device_id = Column(u'device_id', BigInteger(), index=True)
# 	firmware = Column(u'firmware', SmallInteger(), index=True)
# 	hardware = Column(u'hardware', SmallInteger(), index=True)
# 	temp = Column(u'temp', TINYINT(), index=True)
# 	longitude = Column(u'longitude', DOUBLE(), index=True)
# 	latitude = Column(u'latitude', DOUBLE(), index=True)
# 	address = Column(u'address', String(150))
# 	gps_type = Column(u'gps_type', TINYINT(), index=True)
# 	lock_status = Column(u'lock_status', TINYINT(), index=True)
# 	battery_percent = Column(u'battery_percent', TINYINT(), index=True)
# 	mode = Column(u'mode', Integer(), index=True)
# 	abnormal = Column(u'abnormal', TINYINT(), index=True)
# 	faults = Column(u'faults', TINYINT(), index=True)
# 	timestamp = Column(u'timestamp', Integer(), index=True)
# 	ble_key = Column(u'ble_key', String(16), index=True)
# 	upgrade_flag = Column(u'upgrade_flag', TINYINT(), index=True)
# 	update_time = Column(u'update_time', DateTime(), index=True)
#	active = Column(u'active', Boolean(), index=True)

# --------------------------------------------------
# CLASS STATUS_RECORD
# Development.
class StatusRecord(Base):
	'''One device to many records.'''
	__tablename__ = u'status_record'
	__table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8', 'mysql_collate': 'utf8_general_ci'}
	id = Column('id', String(36), primary_key=True) # uuid4
	device_id = Column(u'device_id', BigInteger(), ForeignKey('status.device_id'), index=True)
	lock_status = Column(u'lock_status', Integer(), index=True)
	battery_percent = Column(u'battery_percent', Integer(), index=True)
	mode = Column(u'mode', Integer(), index=True)
	abnormal = Column(u'abnormal', Integer(), index=True)
	faults = Column(u'faults', Integer(), index=True)
	timestamp = Column(u'timestamp', Integer(), index=True)
	create_at = Column(u'create_at', DateTime(), index=True)

	# status = relationship(u'Status', backref='status_records')

# Production.
# class StatusRecord(Base):
# 	'''One device to many records.'''
# 	__tablename__ = u'status_record'
# 	__table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8', 'mysql_collate': 'utf8_general_ci'}
# 	id = Column('id', String(36), primary_key=True) # uuid4
# 	device_id = Column(u'device_id', BigInteger(), ForeignKey('status.device_id'), index=True)
# 	lock_status = Column(u'lock_status', TINYINT(), index=True)
# 	battery_percent = Column(u'battery_percent', TINYINT(), index=True)
# 	mode = Column(u'mode', Integer(), index=True)
# 	abnormal = Column(u'abnormal', TINYINT(), index=True)
# 	faults = Column(u'faults', TINYINT(), index=True)
# 	timestamp = Column(u'timestamp', Integer(), index=True)
# 	create_at = Column(u'create_at', DateTime(), index=True)

# 	# status = relationship(u'Status', backref='status_records')


# --------------------------------------------------
# CLASS CONFIGURATION
# Development and Production.
class Configuration(Base):
	'''One device to one record.'''
	__tablename__ = u'configuration'
	__table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8', 'mysql_collate': 'utf8_general_ci'}
	bike_id = Column(u'bike_id', BigInteger(), primary_key=True)
	device_id = Column(u'device_id', BigInteger(), index=True)
	sim_id = Column(u'sim_id', String(20), index=True)
	phone_id = Column(u'phone_id', String(20), index=True)
	bike_type = Column(u'bike_type', String(10), index=True)
	parameters = Column(u'parameters', String(45), index=True)


# --------------------------------------------------
# CLASS INFORMATION_RECORD
# Development.
class InformationRecord(Base):
	__tablename__ = u'information_record'
	__table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8', 'mysql_collate': 'utf8_general_ci'}
	csq = Column(u'csq', Integer(), primary_key=True)
	temp = Column(u'temp', Integer(), index=True)
	vbus = 	Column(u'vbus', Integer(), index=True)
	charging_status = Column(u'charging_status', Boolean(), index=True)
	vbattery = Column(u'vbattery', Integer(), index=True)
	battery_percent = Column(u'battery_percent', Integer(), index=True)
	create_at = Column(u'create_at', DateTime(), index=True)

# Production.
# class InformationRecord(Base):
# 	__tablename__ = u'information_record'
# 	__table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8', 'mysql_collate': 'utf8_general_ci'}
# 	csq = Column(u'csq', TINYINT(), primary_key=True)
# 	temp = Column(u'temp', TINYINT(), index=True)
# 	vbus = 	Column(u'vbus', TINYINT(), index=True)
# 	charging_status = Column(u'charging_status', Boolean(), index=True)
# 	vbattery = Column(u'vbattery', TINYINT(), index=True)
# 	battery_percent = Column(u'battery_percent', TINYINT(), index=True)
# 	create_at = Column(u'create_at', DateTime(), index=True)


# --------------------------------------------------
# CLASS GPS_RECORD
# Development.
class GpsRecord(Base):
	__tablename__ = u'gps_record'
	__table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8', 'mysql_collate': 'utf8_general_ci'}
	device_id = Column(u'device_id', BigInteger(), primary_key=True)
	longitude = Column(u'longitude', Float(), index=True)
	latitude = Column(u'latitude', Float(), index=True)
	address = Column(u'address', String(150))
	gps_satellite = Column(u'gps_satellite', Integer(), index=True)
	gps_flags = Column(u'gps_flags', Integer(), index=True)
	create_at = Column(u'create_at', DateTime(), index=True)
	is_address_done = Column(u'is_address_done', Integer(), index=True)

# Production
# class GpsRecord(Base):
# 	__tablename__ = u'gps_record'
# 	__table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8', 'mysql_collate': 'utf8_general_ci'}
# 	device_id = Column(u'device_id', BigInteger(), primary_key=True)
# 	longitude = Column(u'longitude', DOUBLE(), index=True)
# 	latitude = Column(u'latitude', DOUBLE(), index=True)
# 	address = Column(u'address', String(150))
# 	gps_satellite = Column(u'gps_satellite', TINYINT(), index=True)
# 	gps_flags = Column(u'gps_flags', TINYINT(), index=True)
# 	create_at = Column(u'create_at', DateTime(), index=True)
# 	is_address_done = Column(u'is_address_done', TINYINT(), index=True)


# --------------------------------------------------
# CLASS ABNORMAL_RECORD
# Development.
class AbnormalRecord(Base):
	__tablename__ = u'abnormal_record'
	__table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8', 'mysql_collate': 'utf8_general_ci'}
	device_id = Column(u'device_id', BigInteger(), primary_key=True)
	abnormal = Column(u'abnormal', Integer(), index=True)
	faults = Column(u'faults', Integer(), index=True)
	create_at = Column(u'create_at', DateTime(), index=True)

# Production
# class AbnormalRecord(Base):
# 	__tablename__ = u'abnormal_record'
# 	__table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8', 'mysql_collate': 'utf8_general_ci'}
# 	device_id = Column(u'device_id', BigInteger(), primary_key=True)
# 	abnormal = Column(u'abnormal', TINYINT(), index=True)
# 	faults = Column(u'faults', TINYINT(), index=True)
# 	create_at = Column(u'create_at', DateTime(), index=True)


# --------------------------------------------------
# CLASS BLE_KEY_RECORD
# Development and Production.
class BleKeyRecord(Base):
	__tablename__ = u'ble_key_record'
	__table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8', 'mysql_collate': 'utf8_general_ci'}
	device_id = Column(u'device_id', BigInteger(), primary_key=True)
	ble_key = Column(u'ble_key', String(16), index=True)
	push_timestamp = Column(u'push_timestamp', Integer(), index=True)
	recv_timestamp = Column(u'recv_timestamp', Integer(), index=True)
	create_at = Column(u'create_at', DateTime(), index=True)






# class Bike(Base):
# 	__tablename__ = u'bike'
# 	__table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8', 'mysql_collate': 'utf8_general_ci'}
# 	id = Column('id', String(16), primary_key=True)


# class Device(Base):
# 	__tablename__ = u'device'
# 	__table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8', 'mysql_collate': 'utf8_general_ci'}
# 	id = Column(u'id', String(16), primary_key=True)
# 	bike_id = Column(u'bike_id', String(16), ForeignKey('bike.id'), index=True)
# 	sim = Column(u'sim', String(20), index=True)
# 	phone = Column(u'phone', String(16), index=True)
# 	ble_key = Column(u'ble_key', String(16), index=True)
# 	parameter = Column(u'parameter', String(12), index=True)
# 	firmware = Column(u'firmware', Integer(), index=True)
# 	hardware = Column(u'hardware', Integer(), index=True)
# 	temp = Column(u'temp', Integer(), index=True)
# 	vbus = Column(u'vbus', Integer(), index=True)
# 	vbattery = Column(u'vbattery', Integer(), index=True)
# 	upgrade_flag = Column(u'upgrade_flag', Integer(), index=True)
# 	scene = Column(u'scene', String(12), index=True)
# 	fault = Column(u'fault', Integer(), index=True)
# 	pedelec = Column(u'pedelec', Integer(), index=True)

# 	bike = relationship(u'Bike', backref='devices')


# class Status(Base):
# 	__tablename__ = u'status'
# 	__table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8', 'mysql_collate': 'utf8_general_ci'}
# 	id = Column(u'id', String(36), primary_key=True)
# 	device_id = Column(u'device_id', String(16), ForeignKey('device.id'), index=True)
# 	longitude = Column(u'longitude', Float(), index=True)
# 	# longitude = Column(u'longitude', DOUBLE(), index=True)
# 	latitude = Column(u'latitude', Float(), index=True)
# 	# latitude = Column(u'latitude', DOUBLE(), index=True)
# 	lock_status = Column(u'lock_status', Integer(), index=True)
# 	csq = Column(u'csq', Integer(), index=True) # GSM Signal Strength
# 	gps_flags = Column(u'gps_flags', Integer(), index=True) # GPS Type
# 	gps_satellite = Column(u'gps_satellite', Integer(), index=True) # Sat Number
# 	battery_percent = Column(u'battery_percent', Integer(), index=True)
# 	battery_charging = Column(u'battery_charging', Integer(), index=True)
# 	mode = Column(u'mode', Integer(), index=True)
# 	start_count = Column(u'start_count', DateTime(), index=True)
# 	last_used = Column(u'last_used', DateTime(), index=True)

# 	device = relationship(u'Device', backref='statuses')



# Auto create if doesnt exist.
Base.metadata.create_all(engine)


# ----------------------------------------------------------

# Initial sample record.

# Create client.
session = Db().Session()
client_id = u'dd8a5f2c-5aac-4ea7-a7a5-db12ebac2a22'
client_secret = u'ba8cfbc9-a75c-404e-9245-80911f3a2a2d'
client = session.query(Client).filter_by(id=client_id).first()
if not client:
	client = Client()
	client.id = client_id
	client.secret = client_secret
	session.add(client)
commit(session)


# Create user.
session = Db().Session()
email = u'fauziwei@yahoo.com'
user = session.query(User).filter_by(email=email).first()
if not user:
	user = User()
	user.id = str(uuid.uuid4())
	user.email = email
	salt = str(uuid.uuid4())
	password = u'123456'

	prepare_password = hashlib.md5(password).hexdigest()
	secure_password = u'{0}{1}'.format(prepare_password, salt)
	hashed_password = hashlib.md5(secure_password).hexdigest()

	user.password = hashed_password
	user.salt = salt
	session.add(user)
commit(session)





# # Create bike
# session = Db().Session()
# bike_id = '1234567812345678'
# bike = session.query(Bike).filter_by(id=bike_id).first()
# if not bike:
# 	bike = Bike()
# 	bike.id = bike_id
# 	session.add(bike)
# commit(session)

# # Create device
# session = Db().Session()
# device_id = '2469040358b6e392'
# device = session.query(Device).filter_by(id=device_id).first()
# if not device:
# 	device = Device()
# 	device.id = device_id
# 	device.bike_id = bike_id
# 	device.sim = '12345678123456781234'
# 	device.phone = '1234567812345678'
# 	device.ble_key = '1234567812345678'
# 	device.parameter = '123456781234'
# 	device.firmware = 1
# 	device.hardware = 1
# 	device.temp = 1
# 	device.vbus = 1
# 	device.vbattery = 1
# 	device.upgrade_flag = 1
# 	device.scene = '123456781234'
# 	device.fault = 0
# 	device.pedelec = 1
# 	session.add(device)
# commit(session)

# # Create status
# session = Db().Session()
# status = session.query(Status).filter_by(device_id=device_id).first()
# if not status:
# 	status = Status()
# 	status.id = str(uuid.uuid4())
# 	status.device_id = device_id
# 	status.longitude = 23.66666666
# 	status.latitude = 3.99999999
# 	status.lock_status = 1
# 	status.csq = 1
# 	status.gps_flags = 1
# 	status.gps_satellite = 1
# 	status.battery_percent = 37
# 	status.battery_charging = 1
# 	status.mode = 1
# 	status.start_count = datetime.datetime.now()
# 	status.last_used = datetime.datetime.now()
# 	session.add(status)
# commit(session)
