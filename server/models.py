# coding: utf-8
# @2017
# Fauzi, fauziwei@yahoo.com
import sys
import traceback
from sqlalchemy import SmallInteger, Integer, BigInteger, \
	Float, String, Boolean, DateTime, \
	Column, Table, ForeignKey, MetaData, create_engine
from sqlalchemy.ext.declarative import declarative_base

# Configuration.
address = '127.0.0.1'
port = 3306
user = 'root'
password = ''
database = 'bikedb'
engine = create_engine('mysql+pymysql://%s:%s@%s:%s/%s?charset=utf8' %
	(user, password, address, port, database))

metadata = MetaData()
Base = declarative_base()

class Db(object):
	'''Session creator.'''
	pass

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
# class Status(Base): pass


# --------------------------------------------------
# CLASS STATUS_RECORD
# class StatusRecord(Base): pass


# --------------------------------------------------
# CLASS ABNORMAL_FAULT_RECORD
# class AbnormalFaultecord(Base): pass


# --------------------------------------------------
# CLASS SYSTEM_UPGRADE_RECORD
# class SystemUpgradeRecord(Base): pass


# --------------------------------------------------
# CLASS GPS_RECORD
# class GpsRecord(Base): pass

# --------------------------------------------------
# CLASS BLE_KEY_RECORD
# class BleKeyRecord(Base): pass

# --------------------------------------------------
# CLASS CONFIGURATION_RECORD
# class ConfigurationRecord(Base): pass


# Auto create if doesnt exist.
Base.metadata.create_all(engine)


# ----------------------------------------------------------

# Initial sample record.
