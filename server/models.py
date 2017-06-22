# coding: utf-8
# @2017
# Fauzi, fauziwei@yahoo.com
import sys
from sqlalchemy import Column, Table, String, DateTime, Integer, Float, Boolean, ForeignKey, MetaData, create_engine
from sqlalchemy.orm  import sessionmaker
from sqlalchemy.pool import NullPool
from sqlalchemy.ext.declarative import declarative_base

reload(sys)
sys.setdefaultencoding('utf-8')

# ---------------------------------------------------
# The following sample for MySQL
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


# ---------------------------------------------------
# The models is started from here...

class Device(Base):
	'''The following only sample table will be created if not exist.'''
	__tablename__ = 'device'
	__table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8', 'mysql_collate': 'utf8_general_ci'}
	id = Column('id', String(36), primary_key=True)
	name = Column('name', String(255), index=True)


# Auto create if doesnt exist.
Base.metadata.create_all(engine)
