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
# MySQL
# address = '127.0.0.1'
# port = 3306
# user = 'your-user'
# password = 'your-password'
# database = 'your-database'
# engine = create_engine('mysql+pymysql://%s:%s@%s:%s/%s?charset=utf8' %
# 	(user, password, address, port, database), encoding='utf8', poolclass=NullPool, echo=False)

# SQLite
engine = create_engine('sqlite:///sqlite.db', encoding='utf8', poolclass=NullPool, echo=False)

metadata = MetaData(engine)

class Db(object):

	def __init__(self):
		self.Session = sessionmaker()
		self.Session.configure(bind=engine)

	@property
	def session(self):
		return self.Session()

class Client(object): pass
class User(object): pass

client_table = Table('client', metadata, autoload=True)
user_table = Table('user', metadata, autoload=True)

mapper(Client, client_table)
mapper(User, user_table)
