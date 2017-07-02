# coding: utf-8
# @2017
# Fauzi, fauziwei@yahoo.com
import sys
from sqlalchemy import create_engine, MetaData, Table, Column, BigInteger
from sqlalchemy.orm  import mapper, sessionmaker
from sqlalchemy.pool import NullPool

reload(sys)
sys.setdefaultencoding('utf-8')

# ---------------------------------------------------
# local database
# SQLite
# engine = create_engine('sqlite:///sqlite.db', encoding='utf8', poolclass=NullPool, echo=False)

# MySQL
address = '127.0.0.1'
port = 3306
user = 'root'
password = ''
database = 'bikedb'
engine = create_engine('mysql+pymysql://%s:%s@%s:%s/%s?charset=utf8' %
	(user, password, address, port, database), encoding='utf8', poolclass=NullPool, echo=False)


metadata = MetaData(bind=engine)

class Db(object):

	def __init__(self):
		self.Session = sessionmaker(autoflush=False)
		self.Session.configure(bind=engine)

	@property
	def session(self):
		return self.Session()

# ---------------------------------------------------

class Client(object): pass
class User(object): pass

class Status(object): pass
class StatusRecord(object): pass
class InformationRecord(object): pass
class GpsRecord(object): pass
class AbnormalRecord(object): pass
class BleKeyRecord(object): pass

# ---------------------------------------------------

client_table = Table('client', metadata, autoload=True)
user_table = Table('user', metadata, Column('id', BigInteger(), primary_key=True, autoincrement=True), autoload=True)

status_table = Table('status', metadata, Column('device_id', BigInteger(), primary_key=True, autoincrement=True), autoload=True)
status_record_table = Table('status_record', metadata, Column('id', BigInteger(), primary_key=True, autoincrement=True), autoload=True)
information_record_table = Table('information_record', metadata, Column('id', BigInteger(), primary_key=True, autoincrement=True), autoload=True)
gps_record_table = Table('gps_record', metadata, Column('id', BigInteger(), primary_key=True, autoincrement=True), autoload=True)
abnormal_record_table = Table('abnormal_record', metadata, Column('id', BigInteger(), primary_key=True, autoincrement=True), autoload=True)
ble_key_record_table = Table('ble_key_record', metadata, Column('id', BigInteger(), primary_key=True, autoincrement=True), autoload=True)

# ---------------------------------------------------

mapper(Client, client_table)
mapper(User, user_table)

mapper(Status, status_table)
mapper(StatusRecord, status_record_table)
mapper(InformationRecord, information_record_table)
mapper(GpsRecord, gps_record_table)
mapper(AbnormalRecord, abnormal_record_table)
mapper(BleKeyRecord, ble_key_record_table)


# ------------------------
session = Db().Session()
clients = session.query(Client).all()
for client in clients:
	print(u'{0}, {1}'.format(client.id, client.secret))

users = session.query(User).all()
for user in users:
	print(u'id: {0}'.format(user.id))
	print(u'email: {0}'.format(user.email))
	print(u'salt: {0}'.format(user.salt))
	print(u'password: {0}'.format(user.password))

session.close()
