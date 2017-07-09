# coding: utf-8
# @2017
# Fauzi, fauziwei@yahoo.com
import os
import time
import pytz
import struct
import ctypes
import select
import socket
import logging
import calendar
import binascii
import datetime
import traceback
import crcmod.predefined
from tornado import web
from Crypto.Cipher import AES
from sqlalchemy.exc import IntegrityError

crc8_func = crcmod.predefined.mkPredefinedCrcFun('crc-8')

logger = logging.getLogger(__name__)

class BaseHandler(web.RequestHandler):
	def __init__(self, *args, **kwargs):
		super(BaseHandler, self).__init__(*args, **kwargs)
