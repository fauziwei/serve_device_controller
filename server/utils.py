# coding: utf-8
# @2017
# Fauzi, fauziwei@yahoo.com
import time
import pytz
import datetime
import struct
import ctypes
import logging
import calendar
import binascii
import crcmod.predefined

logger = logging.getLogger(__name__)

byte_to_hex = lambda b: binascii.hexlify(b)
hex_to_byte = lambda h: binascii.unhexlify(h)

# int_to_hex = lambda i: '0x{0:02x}'.format(i)
int_to_hex = lambda i: '{0:02x}'.format(i)
hex_to_int = lambda h: int(h, 16)

int_to_byte = lambda i: struct.pack('!H', i)[1:]
# int_to_byte = lambda i: struct.pack('!H', i)
# byte_to_int = lambda b: struct.unpack('!H', b)

# double (for latitude and longitude)
double_to_byte = lambda d: struct.pack('d', d)
byte_to_double = lambda b: struct.unpack('d', b)[0]

crc8_func = crcmod.predefined.mkPredefinedCrcFun('crc-8')

def crc8_verification(data):
	cmd = data
	crc8_0xVal = hex(crc8_func(cmd))
	crc8_hex = crc8_0xVal.replace('0x', '')
	crc8_byte = binascii.unhexlify(crc8_hex)
	logger.debug(u'vrfy_crc: {0} , crc: {1}'.format(repr(crc8_byte), repr(data[-1:])))
	return crc8_byte == data[-1:]

def create_crc8_val(data):
	'''data is full data bytesstream arrive from the network.'''
	# crc8_func = crcmod.predefined.mkPredefinedCrcFun('crc-8')
	crc8_0xVal = hex(crc8_func(data))
	crc8_hex = crc8_0xVal.replace('0x', '')
	crc8_byte = binascii.unhexlify(crc8_hex)
	return crc8_byte

def get_shanghai_time():
	return datetime.datetime.now()

def to_timestamp(t):
	'''
	t = get_shanghai_time()
	ts = to_timestamp(t)
	'''
	return time.mktime(t)

def timestamp_to_byte(ts):
	return struct.pack('<I', ts)
