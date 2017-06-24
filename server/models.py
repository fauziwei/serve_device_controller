# coding: utf-8
# @2017
# Fauzi, fauziwei@yahoo.com
import sys
import traceback
from sqlalchemy import String, Integer, Float, Boolean, \
	Column, Table, ForeignKey, MetaData, create_engine
from sqlalchemy.dialects.mysql import DOUBLE
from sqlalchemy.orm  import sessionmaker
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

class Device(Base):
	'''The following only sample table will be created if not exist.'''
	__tablename__ = 'device'
	__table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8', 'mysql_collate': 'utf8_general_ci'}
	id = Column('id', String(16), primary_key=True)
	# work/test/maintain
	mode = Column('mode', Integer(), index=True)
	firmware = Column('firmware', Integer(), index=True)
	hardware = Column('hardware', Integer(), index=True)
	# longitude = Column('longitude', DOUBLE(), index=True)
	longitude = Column('longitude', Float(), index=True)
	# latitude = Column('latitude', DOUBLE(), index=True)
	latitude = Column('latitude', Float(), index=True)
	# gps data type
	gps_flags = Column('gps_flags', Integer(), index=True)
	# satellite number
	gps_satellite = Column('gps_satellite', Integer(), index=True)
	lock_status = Column('lock_status', Integer(), index=True)
	battery = Column('battery', Integer(), index=True)
	# charging status
	charging = Column('charging', Integer(), index=True)
	ble_key = Column('ble_key', String(16), index=True)
	# GSM signal strength
	csq = Column('csq', Integer(), index=True)
	# sim card ID
	sim = Column('sim', String(20), index=True)
	# phone number with sms
	phone = Column('phone', String(16), index=True)
	upgrade_flag = Column('upgrade_flag', Integer(), index=True)
	parameters = Column('parameters', String(12), index=True)
	scene = Column('scene', String(12), index=True)



# Auto create if doesnt exist.
Base.metadata.create_all(engine)
