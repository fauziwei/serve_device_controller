# coding: utf-8
# @2017
# Fauzi, fauziwei@yahoo.com
import sys
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm  import mapper, sessionmaker
from sqlalchemy.pool import NullPool

reload(sys)
sys.setdefaultencoding('utf-8')

# ---------------------------------------------------
# local database
# SQLite
engine = create_engine('sqlite:///sqlite.db', encoding='utf8', poolclass=NullPool, echo=False)

# MySQL
# address = '127.0.0.1'
# port = 3306
# user = 'your-user'
# password = 'your-password'
# database = 'your-database'
# engine = create_engine('mysql+pymysql://%s:%s@%s:%s/%s?charset=utf8' %
# 	(user, password, address, port, database), encoding='utf8', poolclass=NullPool, echo=False)


metadata = MetaData(engine)

class Db(object):

	def __init__(self):
		self.Session = sessionmaker()
		self.Session.configure(bind=engine)

	@property
	def session(self):
		return self.Session()

# ---------------------------------------------------

class Client(object): pass
class User(object): pass

class Status(object): pass
class StatusRecord(object): pass
class Configuration(object): pass
class InformationRecord(object): pass
class GpsRecord(object): pass
class AbnormalRecord(object): pass
class BleKeyRecord(object): pass

# ---------------------------------------------------

client_table = Table('client', metadata, autoload=True)
user_table = Table('user', metadata, autoload=True)

status_table = Table('status', metadata, autoload=True)
status_record_table = Table('status_record', metadata, autoload=True)
configuration_table = Table('configuration', metadata, autoload=True)
information_record_table = Table('information_record', metadata, autoload=True)
gps_record_table = Table('gps_record', metadata, autoload=True)
abnormal_record_table = Table('abnormal_record', metadata, autoload=True)
ble_key_record_table = Table('ble_key_record', metadata, autoload=True)

# ---------------------------------------------------

mapper(Client, client_table)
mapper(User, user_table)

mapper(Status, status_table)
mapper(StatusRecord, status_record_table)
mapper(Configuration, configuration_table)
mapper(InformationRecord, information_record_table)
mapper(GpsRecord, gps_record_table)
mapper(AbnormalRecord, abnormal_record_table)
mapper(BleKeyRecord, ble_key_record_table)
