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

# ---------------------------------------------------

class Client(object): pass
class User(object): pass

class Status(object): pass
class StatusRecord(object): pass
class InformationRecord(object): pass
class GpsRecord(object): pass
class AbnormalRecord(object): pass
class BleKeyRecord(object): pass
