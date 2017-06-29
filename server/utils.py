# coding: utf-8
# @2017
# Fauzi, fauziwei@yahoo.com
import time
import pytz
import datetime
import struct
import ctypes
import logging
import binascii
import crcmod.predefined

logger = logging.getLogger(__name__)

byte_to_hex = lambda b: binascii.hexlify(b)
hex_to_byte = lambda h: binascii.unhexlify(h)

# int_to_hex = lambda i: '0x{0:02x}'.format(i)
int_to_hex = lambda i: '{0:02x}'.format(i)
hex_to_int = lambda h: int(h, 16)

int_to_byte = lambda i: struct.pack('!H', i)[1:]

float_to_byte = lambda f: struct.pack('f', f)
byte_to_float = lambda b: struct.unpack('f', b)[0]

# double (for latitude and longitude)
double_to_byte = lambda f: struct.pack('>d', f)
byte_to_double = lambda b: struct.unpack('>d', byte)[0]

int32_to_uint32 = lambda i: ctypes.c_uint32(i).value
ascii_string = lambda s: ''.join(map(lambda c: "%02X " % ord(c), s))

crc8_func = crcmod.predefined.mkPredefinedCrcFun('crc-8')

def convert_length_to_byte(int_len):
	if int_len > 0xFF:
		high = int_len & 0xFF
		low = int_len >> 8
		str_len = chr(low) + chr(high)
	else:
		str_len = '\x00' + chr(int_len)
	return str_len

def crc8_verification(data):
	cmd = data[:-1]
	# crc8_func = crcmod.predefined.mkPredefinedCrcFun('crc-8')
	# crc8_0xVal = hex(crc8_func(cmd))
	# crc8_hex = crc8_0xVal.replace('0x', '')
	crc8_hex = int_to_hex(crc8_func(cmd))
	crc8_byte = binascii.unhexlify(crc8_hex)
	logger.debug('vrfy_crc: {0} , crc: {1}'.format(repr(crc8_byte), repr(data[-1:])))
	return crc8_byte == data[-1:]

def create_crc8_val(data):
	'''data is full data bytesstream arrive from the network.'''
	# crc8_func = crcmod.predefined.mkPredefinedCrcFun('crc-8')
	# crc8_0xVal = hex(crc8_func(data))
	# crc8_hex = crc8_0xVal.replace('0x', '')
	crc8_hex = int_to_hex(crc8_func(data))
	crc8_byte = binascii.unhexlify(crc8_hex)
	return crc8_byte

def get_shanghai_time():
	tz = pytz.timezone('Asia/Shanghai')
	return datetime.datetime.now(tz)

def to_timestamp(t):
	'''
	t = get_shanghai_time()
	ts = to_timestamp(t)
	'''
	return round( time.mktime(t.timetuple()) )

def timestamp_to_byte(ts):
	return struct.pack('<I', ts)
