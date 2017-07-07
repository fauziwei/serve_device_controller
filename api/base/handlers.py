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

		self.START = '\xAA'

		self.CLIENT_TYPE = {
		  'heartbeat'             : '\x01',
		  'normal_ack'            : '\x02', # client/server has normal_ack
		  # 'lock_control'          : '\x10',
		  'lock_unlock_response'  : '\x13',
		  'gps_data_report'       : '\x32',
		  'normal_bike_status'    : '\x42',
		  'pedelec_status_report' : '\x43',
		  'fault_report'          : '\x44',
		  'ble_key_response'      : '\x52',
		  'command_response'      : '\x62',
		  'upgrade_push_response' : '\x72',
		  'upgrade_data_request'  : '\x73'
		}

		self.SERVER_TYPE = {
		  'normal_ack'            : '\x02', # client/server has normal_ack
		  # 'lock_control'          : '\x10',
		  'unlock'                : '\x11',
		  'lock'                  : '\x12',
		  'configuration_command' : '\x21',
		  'fire_gps_starting_up'  : '\x31',
		  'get_device_status'     : '\x41',
		  'ble_key_update'        : '\x51',
		  'control_command_send'  : '\x61',
		  'upgrade_command_push'  : '\x71',
		  'upgrade_data_send'     : '\x74'
		}

		self.aes_key = self.settings.get('aes_key')
		self.delimiter = self.settings.get('delimiter')
		self.timeout = self.settings.get('timeout')
		self.controller_start = self.settings.get('controller_start')
		self.response_fail = self.settings.get('response_fail')
		self.response_success = self.settings.get('response_success')

	@property
	def devices_cache(self):
		return self.application.devices_cache

	@property
	def access_token_cache(self):
		return self.application.access_token_cache

	@property
	def models(self):
		return self.application.models

	def commit(self, session):
		try:
			session.flush()
			session.commit()
		except IntegrityError:
			session.rollback()
			logger.debug(u'Exception IntegrityError.')
		except:
			traceback.print_exc()
			session.rollback()
			logger.debug(u'Exception commit.')
		finally:
			session.close()

	def aes_encrypt(self, data):
		'''data is without crc. Only 16bytes.'''
		IV = os.urandom(16)
		aes = AES.new(self.aes_key, AES.MODE_ECB, IV=IV)
		ciphertext = aes.encrypt(data)
		return ciphertext

	def aes_decrypt(self, data):
		'''data is without crc. Only 16bytes.'''
		IV = os.urandom(16)
		aes = AES.new(self.aes_key, AES.MODE_ECB, IV=IV)
		text = aes.decrypt(data)
		return text

	def convert_length_to_byte(self, int_len):
		if int_len > 0xFF:
			high = int_len & 0xFF
			low = int_len >> 8
			str_len = chr(low) + chr(high)
		else:
			str_len = '\x00' + chr(int_len)
		return str_len

	byte_to_hex = lambda self, b: binascii.hexlify(b)
	hex_to_byte = lambda self, h: binascii.unhexlify(h)

	# int_to_hex = lambda self, i: '0x{0:02x}'.format(i)
	int_to_hex = lambda self, i: '{0:02x}'.format(i)
	hex_to_int = lambda self, h: int(h, 16)

	int_to_byte = lambda self, i: struct.pack('!H', i)[1:]
	# int_to_byte = lambda self, i: struct.pack('!H', i)
	# byte_to_int = lambda self, b: struct.unpack('!H', b)

	float_to_byte = lambda self, f: struct.pack('f', f)
	byte_to_float = lambda self, b: struct.unpack('f', b)[0]

	# double (for latitude and longitude)
	double_to_byte = lambda self, f: struct.pack('>d', f)
	byte_to_double = lambda self, b: struct.unpack('>d', byte)[0]

	int32_to_uint32 = lambda self, i: ctypes.c_uint32(i).value
	ascii_string = lambda self, s: ''.join(map(lambda c: "%02X " % ord(c), s))

	def crc8_verification(self, data):
		cmd = data[:-1]
		# crc8_func = crcmod.predefined.mkPredefinedCrcFun('crc-8')
		# crc8_0xVal = hex(crc8_func(cmd))
		# crc8_hex = crc8_0xVal.replace('0x', '')
		crc8_hex = self.int_to_hex(crc8_func(cmd))
		crc8_byte = binascii.unhexlify(crc8_hex)
		logger.debug(u'vrfy_crc: {0} , crc: {1}'.format(repr(crc8_byte), repr(data[-1:])))
		return crc8_byte == data[-1:]

	def create_crc8_val(self, data):
		'''data is full data ByteStream arrive from the network.'''
		# crc8_func = crcmod.predefined.mkPredefinedCrcFun('crc-8')
		# crc8_0xVal = hex(crc8_func(data))
		# crc8_hex = crc8_0xVal.replace('0x', '')
		crc8_hex = self.int_to_hex(crc8_func(data))
		crc8_byte = binascii.unhexlify(crc8_hex)
		return crc8_byte

	def get_shanghai_time(self):
		tz = pytz.timezone('Asia/Shanghai')
		return datetime.datetime.now(tz)

	def to_timestamp(self, t):
		'''
		t = get_shanghai_time()
		ts = to_timestamp(t)
		'''
		# return round( time.mktime(t.timetuple()) )
		return round( calendar.timegm(t.timetuple()) )

	def timestamp_to_byte(self, ts):
		return struct.pack('<I', ts)

	def get_version(self, version):
		return self.hex_to_byte(self.int_to_hex(version))

	def get_message_id(self, message_id):
		'''Integer to ByteStream.
		It supposed to be increased by one.
		'''
		return self.hex_to_byte(self.int_to_hex(message_id))

	def get_firmware(self, firmware):
		return self.hex_to_byte(self.int_to_hex(firmware))

	def get_controller_id(self, controller_id):
		return self.hex_to_byte(self.int_to_hex(controller_id))

	def get_length(self, version, message_type, message_id, firmware, controller_id):
		'''
		version = integer,
		message_type = byte,
		message_id = integer,
		firmware = integer,
		controller_id = integer
		'''
		length = len(self.START)+2+len(self.get_version(version))+len(message_type)+\
			len(self.get_message_id(message_id))+len(self.get_firmware(firmware))+\
			len(self.get_controller_id(controller_id))
		return self.convert_length_to_byte(length)


class SetupConnection(object):

	def __init__(self, *args, **kwargs):

		self.delimiter = kwargs['delimiter']
		self.timeout = kwargs['timeout']
		self.server_ip = kwargs['server_ip']
		self.server_port = kwargs['server_port']

	def send(self, s):
		try:
			logger.debug(u'Send: {0}'.format(repr(s)))
			self.s.send(s+self.delimiter)
		except socket.error:
			self.s.close()
			# logger.debug(u'Fails send to server: {0}'.format(s))
			return 
		return 'Sent'

	def recv(self):
		ready = select.select([self.s], [], [], self.timeout)
		if not ready[0]:
			self.s.close()
			reason = u'Read timeout > {0} seconds.'.format(self.timeout)
			logger.debug(reason)
			return
		
		data = self.s.recv(1024)
		logger.debug(u'Recv: {0}'.format(repr(data)))
		if not data:
			reason = u'No reply from server. Fails setup device.'
			logger.debug(reason)
			return
		return data

	def connect(self):
		self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		try:
			self.s.connect((self.server_ip, self.server_port))
			self.s.setblocking(True)
		except socket.error:
			self.s.close()
			# logger.debug(u'Fails get connection to server.')
			return
		return 'Connect'

	def close(self):
		self.s.close()
