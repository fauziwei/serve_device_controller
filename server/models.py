# coding: utf-8
# @2017
# Fauzi, fauziwei@yahoo.com
import sys
import uuid
import hashlib
import traceback
from sqlalchemy import SmallInteger, Integer, BigInteger, \
	Float, String, Boolean, DateTime, \
	Column, Table, ForeignKey, MetaData, create_engine
from sqlalchemy import SMALLINT, INTEGER, BIGINT, VARCHAR
from sqlalchemy.dialects.mysql import DOUBLE, TINYINT
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.exc import IntegrityError
from sqlalchemy.pool import NullPool
from sqlalchemy.ext.declarative import declarative_base

reload(sys)
sys.setdefaultencoding('utf-8')


# Configuration.
address = '127.0.0.1'
port = 3306
user = 'root'
password = ''
database = 'bikedb'
engine = create_engine('mysql+pymysql://%s:%s@%s:%s/%s?charset=utf8' %
	(user, password, address, port, database), encoding='utf8', poolclass=NullPool, echo=False)


metadata = MetaData(bind=engine)
Base = declarative_base(metadata=metadata)


class Db(object):
	'''Session creator.'''

	def __init__(self):
		self.Session = sessionmaker(autoflush=False)
		self.Session.configure(bind=engine)

	@property
	def session(self):
		return self.Session()


def commit(session):
	try:
		session.flush()
		session.commit()
	except IntegrityError:
		session.rollback()
	except:
		traceback.print_exc()
		session.rollback()
	finally:
		session.close()


# ---------------------------------------------------
# The models is started from here...
# --------------------------------------------------

class Client(Base):
	'''Client application.
	Purposed for Oauth2 client_id and client_secret.
	One to one record.
	'''
	__tablename__ = u'client'
	__table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8', 'mysql_collate': 'utf8_general_ci'}
	id = Column('id', String(36), primary_key=True) # uuid4
	secret = Column('secret', String(36), index=True, nullable=False) # uuid4


class User(Base):
	'''User controller.
	Table for Login user.
	One to one record.
	'''
	__tablename__ = u'user'
	__table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8', 'mysql_collate': 'utf8_general_ci'}
	id = Column('id', BigInteger(), primary_key=True, autoincrement=True)
	email = Column('email', String(150), index=True, unique=True, nullable=False)
	salt = Column('salt', String(36), index=True, nullable=False) # uuid4
	password = Column('password', String(32), index=True, nullable=False) # md5


# --------------------------------------------------
# CLASS STATUS
class Status(Base):
	'''One device to one record.
	This table is parent's table of all bike sharing's tables.
	'''
	__tablename__ = u'status'
	__table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8', 'mysql_collate': 'utf8_general_ci'}
	device_id = Column(u'device_id', BigInteger(), primary_key=True)
	bike_id = Column(u'bike_id', BigInteger(), index=True)
	sim_id = Column(u'sim_id', String(20), index=True)
	phone_id = Column(u'phone_id', String(20), index=True)
	bike_type = Column(u'bike_type', String(10), index=True)
	parameters = Column(u'parameters', String(100), index=True)
	firmware = Column(u'firmware', SmallInteger(), index=True)
	hardware = Column(u'hardware', SmallInteger(), index=True)
	hdware_ver = Column(u'hdware_ver', SmallInteger(), index=True)
	timestamp = Column(u'timestamp', Integer(), index=True)
	upgrade_flag = Column(u'upgrade_flag', TINYINT(1), index=True)
	lock_status = Column(u'lock_status', TINYINT(1), index=True)
	csq = Column(u'csq', TINYINT(1), index=True)
	temp = Column(u'temp', TINYINT(1), index=True)
	vbus = 	Column(u'vbus', TINYINT(1), index=True)
	icharge = Column(u'icharge', Boolean(), index=True) # charging status
	vbattery = Column(u'vbattery', Integer(), index=True)
	battery_stat = Column(u'battery_stat', SmallInteger(), index=True) # battery percentage
	latitude = Column(u'latitude', DOUBLE(), index=True)
	longitude = Column(u'longitude', DOUBLE(), index=True)
	fix_flag = Column(u'fix_flag', TINYINT(1), index=True)
	gps_stars = Column(u'gps_stars', TINYINT(1), index=True)
	signature = Column(u'signature', TINYINT(1), index=True)
	ride_speed = Column(u'ride_speed', SmallInteger(), index=True)
	limit_speed = Column(u'limit_speed', SmallInteger(), index=True)
	gear = Column(u'gear', TINYINT(1), index=True)
	m_vbattery = Column(u'm_vbattery', Integer(), index=True)
	m_battery_stat = Column(u'm_battery_stat', SmallInteger(), index=True)
	m_battery_cab = Column(u'm_battery_cab', SmallInteger(), index=True)
	m_bat_is = Column(u'm_bat_is', Boolean(), index=True) # 0 = offline, 1 = online
	m_bat_cycle = Column(u'm_bat_cycle', SmallInteger(), index=True) # charge cycles / cycles count
	m_bat_temp = Column(u'm_bat_temp', SmallInteger(), index=True) # Charge temperature
	m_bat_id = Column(u'm_bat_id', Integer(), index=True)
	abnormal = Column(u'abnormal', TINYINT(1), index=True)
	fault = Column(u'fault', TINYINT(1), index=True)
	ble_key = Column(u'ble_key', String(16), index=True)
	address = Column(u'address', String(150))
	gps_flags = Column(u'gps_flags', TINYINT(1), index=True)
	mode = Column(u'mode', Integer(), index=True)
	update_time = Column(u'update_time', DateTime(), index=True)
	active = Column(u'active', Boolean(), default=True, index=True)


# --------------------------------------------------
# CLASS STATUS_RECORD
class StatusRecord(Base):
	'''One device to many records.'''
	__tablename__ = u'status_record'
	__table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8', 'mysql_collate': 'utf8_general_ci'}
	id = Column('id', BigInteger(), primary_key=True, autoincrement=True)
	device_id = Column(u'device_id', BigInteger(), ForeignKey('status.device_id'), index=True)
	lock_status = Column(u'lock_status', TINYINT(1), index=True)
	battery_stat = Column(u'battery_stat', SmallInteger(), index=True)
	mode = Column(u'mode', Integer(), index=True)
	abnormal = Column(u'abnormal', TINYINT(1), index=True)
	fault = Column(u'fault', TINYINT(1), index=True)
	timestamp = Column(u'timestamp', Integer(), index=True)
	create_at = Column(u'create_at', DateTime(), index=True)

	status = relationship(u'Status', backref='status_records')


# --------------------------------------------------
# CLASS INFORMATION_RECORD
class InformationRecord(Base):
	'''One device to many records.'''
	__tablename__ = u'information_record'
	__table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8', 'mysql_collate': 'utf8_general_ci'}
	id = Column('id', BigInteger(), primary_key=True, autoincrement=True)
	device_id = Column(u'device_id', BigInteger(), ForeignKey('status.device_id'), index=True)
	csq = Column(u'csq', TINYINT(1), index=True)
	temp = Column(u'temp', TINYINT(1), index=True)
	vbus = 	Column(u'vbus', TINYINT(1), index=True)
	icharge = Column(u'icharge', Boolean(), index=True) # charging status
	vbattery = Column(u'vbattery', Integer(), index=True)
	battery_stat = Column(u'battery_stat', SmallInteger(), index=True)
	create_at = Column(u'create_at', DateTime(), index=True)

	status = relationship(u'Status', backref='information_records')


# --------------------------------------------------
# CLASS GPS_RECORD
class GpsRecord(Base):
	'''One device to many records.'''
	__tablename__ = u'gps_record'
	__table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8', 'mysql_collate': 'utf8_general_ci'}
	id = Column('id', BigInteger(), primary_key=True, autoincrement=True)
	device_id = Column(u'device_id', BigInteger(), ForeignKey('status.device_id'), index=True)
	longitude = Column(u'longitude', DOUBLE(), index=True)
	latitude = Column(u'latitude', DOUBLE(), index=True)
	gps_satellite = Column(u'gps_satellite', TINYINT(1), index=True)
	gps_stars = Column(u'gps_stars', TINYINT(1), index=True)
	gps_flags = Column(u'gps_flags', TINYINT(1), index=True)
	create_at = Column(u'create_at', DateTime(), index=True)
	is_address_done = Column(u'is_address_done', Boolean(), index=True)

	status = relationship(u'Status', backref='gps_records')


# --------------------------------------------------
# CLASS ABNORMAL_RECORD
class AbnormalRecord(Base):
	'''One device to many records.'''
	__tablename__ = u'abnormal_record'
	__table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8', 'mysql_collate': 'utf8_general_ci'}
	id = Column('id', BigInteger(), primary_key=True, autoincrement=True)
	device_id = Column(u'device_id', BigInteger(), ForeignKey('status.device_id'), index=True)
	abnormal = Column(u'abnormal', TINYINT(1), index=True)
	fault = Column(u'fault', TINYINT(1), index=True)
	create_at = Column(u'create_at', DateTime(), index=True)

	status = relationship(u'Status', backref='abnormal_records')


# --------------------------------------------------
# CLASS BLE_KEY_RECORD
class BleKeyRecord(Base):
	'''One device to many records.'''
	__tablename__ = u'ble_key_record'
	__table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8', 'mysql_collate': 'utf8_general_ci'}
	id = Column('id', BigInteger(), primary_key=True, autoincrement=True)
	device_id = Column(u'device_id', BigInteger(), ForeignKey('status.device_id'), index=True)
	ble_key = Column(u'ble_key', String(16), index=True)
	push_timestamp = Column(u'push_timestamp', Integer(), index=True)
	recv_timestamp = Column(u'recv_timestamp', Integer(), index=True)
	create_at = Column(u'create_at', DateTime(), index=True)

	status = relationship(u'Status', backref='ble_key_records')

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
	# user.id = 1
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
