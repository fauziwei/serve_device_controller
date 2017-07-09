# coding: utf-8
# @2017
# Fauzi, fauziwei@yahoo.com
import sys
import json
import logging
import datetime
from tornado import gen, web
# local import

reload(sys)
sys.setdefaultencoding('utf-8')

logger = logging.getLogger(__name__)


class UnLock(BaseHandler):
	'''Initiate sending unlock message.'''

class Lock(BaseHandler):
	'''Initiate sending lock message.'''


class FireGpsStartingUp(BaseHandler):
	'''Initiate sending fire_gps_starting_up message.'''


class BleKeyUpdate(BaseHandler):
	'''Initiate sending ble_key_update message.'''
