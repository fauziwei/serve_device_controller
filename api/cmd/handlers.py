# coding: utf-8
# @2017
# Fauzi, fauziwei@yahoo.com
import sys
import json
import logging
import datetime
from tornado import gen, web
# local import
from base.handlers import BaseHandler, SetupConnection
from lib.decorator import access_token

reload(sys)
sys.setdefaultencoding('utf-8')

logger = logging.getLogger(__name__)


class UnLock(BaseHandler):
	'''Initiate sending unlock message.'''

	@web.asynchronous
	@gen.engine
	@access_token
	def post(self, *args, **kwargs):
		payload = json.loads(self.request.body)

		version = payload.get('version', None)
		message_id = payload.get('message_id', None)
		firmware = payload.get('firmware', None)
		controller_id = payload.get('controller_id', None)
		signature = payload.get('signature', None)

		if version == '': version = None
		if message_id == '': message_id = None
		if firmware == '': firmware = None
		if controller_id == '': controller_id = None
		if signature == '': signature = None

		message_type = self.SERVER_TYPE['unlock']

		logger.debug( 30 * u'-' )
		logger.debug(u'Post unlock:')
		logger.debug(u'version: {0}'.format(version))
		logger.debug(u'message_id: {0}'.format(message_id))
		logger.debug(u'firmware: {0}'.format(firmware))
		logger.debug(u'controller_id: {0}'.format(controller_id))
		logger.debug(u'signature: {0}'.format(signature))
		logger.debug(u'message_type: {0}'.format(repr(version)))

		if version is None or \
			message_id is None or \
			firmware is None or \
			controller_id is None or \
			signature is None:
			reason = u'required version(int), message_id(int), firmware(int), controller_id(int), signature(int).'
			logger.debug(reason)
			self.finish( json.dumps({'success': False, 'reason': reason}) )
			return

		try:
			version = int(version)
			message_id = int(message_id)
			firmware = int(firmware)
			controller_id = int(controller_id)
			signature = int(signature)
		except:
			reason = u'Exception conversion from unicode string to integer.'
			logger.debug(reason)
			self.finish( json.dumps({'success': False, 'reason': reason}) )
			return

		d = yield gen.Task(self.post_pool, version, message_type, message_id, firmware, controller_id, signature)
		self.finish( json.dumps({'success': d['success'], 'reason': d['reason']}) )

	def post_pool(self, version, message_type, message_id, firmware, controller_id, signature, callback):

		length = self.get_length(version, message_type, message_id, firmware, controller_id)

		# header ---------------------------------
		header = self.START+\
			length+\
			self.get_version(version)+\
			message_type+\
			self.get_message_id(message_id)+\
			self.get_firmware(firmware)+\
			self.get_controller_id(controller_id)

		# payload --------------------------------

		# start_timestamp (4bytes)
		t = self.get_shanghai_time()
		start_timestamp = self.to_timestamp(t)
		start_timestamp = self.timestamp_to_byte(start_timestamp)

		# end_timestamp (4bytes)
		# start + 2 minutes
		future_t = t + datetime.timedelta(minutes=2)
		end_timestamp = self.to_timestamp(future_t)
		end_timestamp = self.timestamp_to_byte(end_timestamp)

		zeros = '\x00' * 7
		# signature = 1
		payload = \
			end_timestamp+\
			start_timestamp+\
			zeros+\
			self.hex_to_byte(self.int_to_hex(signature))

		# -----------------------------------------------

		logger.debug( 30 * u'-' )
		logger.debug(u'header: {0}'.format(repr(header)))
		logger.debug(u'header length: {0}'.format(len(header)))
		logger.debug( 30 * u'-' )
		logger.debug(u'payload before aes: {0}'.format(repr(payload)))
		logger.debug(u'payload length: {0}'.format(len(payload)))
		logger.debug( 30 * u'-' )

		# aes encryption
		payload = self.aes_encrypt(payload)
		payload = payload.replace('\n', '\x0D') # Check.
		logger.debug(u'payload after aes: {0}'.format(repr(payload)))
		logger.debug(u'payload length: {0}'.format(len(payload)))
		logger.debug( 30 * u'-' )

		# create crc8
		cmd = header+payload
		crc8_byte = self.create_crc8_val(cmd)
		unlock = cmd+crc8_byte

		logger.debug(u'unlock: {0}'.format(repr(unlock)))
		logger.debug(u'unlock length: {0}'.format(len(unlock)))
		logger.debug( 30 * u'-' )

		if not self.crc8_verification(unlock):
			reason = u'CRC8 verification error before sending unlock message. Exit!'
			logger.debug(reason)
			d = {'success': False, 'reason': reason}
			return callback(d)


		# Check redis cache for device connected.
		addr_port = self.devices_cache.get(controller_id)
		if not addr_port:
			reason = u'Device: {0} doesnt exist in redis/ maybe disconnected.'.format(controller_id)
			logger.debug(reason)
			d = {'success': False, 'reason': reason}
			return callback(d)
		addr, port = addr_port.split(':')
		port = int(port)

		# Setup connection and do interaction with server.
		d = {
			'delimiter': self.delimiter,
			'timeout': self.timeout,
			'server_ip': addr,
			'server_port': port
		}

		logger.debug( 30 * u'-' )
		logger.debug(u'Start setting up connection to server: {0}:{1}'.format(addr, port))

		control = SetupConnection(**d)

		# create connection.
		connect = control.connect()
		if not connect:
			reason = u'Fails get connection to server: {0}:{1}.'.format(addr, port)
			logger.debug(reason)
			d = {'success': False, 'reason': reason}
			return callback(d)
		logger.debug(u'Success get connection to server...')

		# sending message.
		sendto = control.send(unlock)
		if not sendto:
			reason = u'Fails sending message to server: {0}:{1}'.format(addr, port)
			logger.debug(reason)
			d = {'success': False, 'reason': reason}
			return callback(d)
		logger.debug(u'Success sending message to server...')

		# receive message.
		recv = control.recv()
		if not recv:
			reason = u'Fails get response from server: {0}:{1}'.format(addr, port)
			logger.debug(reason)
			d = {'success': False, 'reason': reason}
			return callback(d)

		if recv == self.response_success:
			reason = u'Success setup device.'
		elif recv == self.response_fail:
			reason = u'Fails setup device.'
		else:
			reason = u'Error get message response.'
		
		logger.debug(reason)
		logger.debug('Initiate to drop connection.')
		control.close()
		d = {'success': True, 'reason': reason}
		return callback(d)


class Lock(BaseHandler):
	'''Initiate sending lock message.'''

	@web.asynchronous
	@gen.engine
	@access_token
	def post(self, *args, **kwargs):
		payload = json.loads(self.request.body)

		version = payload.get('version', None)
		message_id = payload.get('message_id', None)
		firmware = payload.get('firmware', None)
		controller_id = payload.get('controller_id', None)
		signature = payload.get('signature', None)

		if version == '': version = None
		if message_id == '': message_id = None
		if firmware == '': firmware = None
		if controller_id == '': controller_id = None
		if signature == '': signature = None

		message_type = self.SERVER_TYPE['lock']

		logger.debug( 30 * u'-' )
		logger.debug(u'Post lock:')
		logger.debug(u'version: {0}'.format(version))
		logger.debug(u'message_id: {0}'.format(message_id))
		logger.debug(u'firmware: {0}'.format(firmware))
		logger.debug(u'controller_id: {0}'.format(controller_id))
		logger.debug(u'signature: {0}'.format(signature))
		logger.debug(u'message_type: {0}'.format(repr(version)))

		if version is None or \
			message_id is None or \
			firmware is None or \
			controller_id is None or \
			signature is None:
			reason = u'required version(int), message_id(int), firmware(int), controller_id(int), signature(int).'
			logger.debug(reason)
			self.finish( json.dumps({'success': False, 'reason': reason}) )
			return

		try:
			version = int(version)
			message_id = int(message_id)
			firmware = int(firmware)
			controller_id = int(controller_id)
			signature = int(signature)
		except:
			reason = u'Exception conversion from unicode string to integer.'
			logger.debug(reason)
			self.finish( json.dumps({'success': False, 'reason': reason}) )
			return

		d = yield gen.Task(self.post_pool, version, message_type, message_id, firmware, controller_id, signature)
		self.finish( json.dumps({'success': d['success'], 'reason': d['reason']}) )

	def post_pool(self, version, message_type, message_id, firmware, controller_id, signature, callback):

		length = self.get_length(version, message_type, message_id, firmware, controller_id)

		# header ---------------------------------
		header = self.START+\
			length+\
			self.get_version(version)+\
			message_type+\
			self.get_message_id(message_id)+\
			self.get_firmware(firmware)+\
			self.get_controller_id(controller_id)

		# payload --------------------------------

		zeros = '\x00' * 15
		# signature = 1
		payload = \
			zeros+\
			self.hex_to_byte(self.int_to_hex(signature))

		# -----------------------------------------------

		logger.debug( 30 * u'-' )
		logger.debug(u'header: {0}'.format(repr(header)))
		logger.debug(u'header length: {0}'.format(len(header)))
		logger.debug( 30 * u'-' )
		logger.debug(u'payload before aes: {0}'.format(repr(payload)))
		logger.debug(u'payload length: {0}'.format(len(payload)))
		logger.debug( 30 * u'-' )

		# aes encryption
		payload = self.aes_encrypt(payload)
		payload = payload.replace('\n', '\x0D') # Check.
		logger.debug(u'payload after aes: {0}'.format(repr(payload)))
		logger.debug(u'payload length: {0}'.format(len(payload)))
		logger.debug( 30 * u'-' )

		# create crc8
		cmd = header+payload
		crc8_byte = self.create_crc8_val(cmd)
		lock = cmd+crc8_byte

		logger.debug(u'lock: {0}'.format(repr(lock)))
		logger.debug(u'lock length: {0}'.format(len(lock)))
		logger.debug( 30 * u'-' )

		if not self.crc8_verification(lock):
			reason = u'CRC8 verification error before sending lock message. Exit!'
			logger.debug(reason)
			d = {'success': False, 'reason': reason}
			return callback(d)

		# sending socket.


class FireGpsStartingUp(BaseHandler):
	'''Initiate sending fire_gps_starting_up message.'''

	@web.asynchronous
	@gen.engine
	@access_token
	def post(self, *args, **kwargs):
		payload = json.loads(self.request.body)

		version = payload.get('version', None)
		message_id = payload.get('message_id', None)
		firmware = payload.get('firmware', None)
		controller_id = payload.get('controller_id', None)
		signature = payload.get('signature', None)

		if version == '': version = None
		if message_id == '': message_id = None
		if firmware == '': firmware = None
		if controller_id == '': controller_id = None
		if signature == '': signature = None

		message_type = self.SERVER_TYPE['fire_gps_starting_up']

		logger.debug( 30 * u'-' )
		logger.debug(u'Post fire_gps_starting_up:')
		logger.debug(u'version: {0}'.format(version))
		logger.debug(u'message_id: {0}'.format(message_id))
		logger.debug(u'firmware: {0}'.format(firmware))
		logger.debug(u'controller_id: {0}'.format(controller_id))
		logger.debug(u'signature: {0}'.format(signature))
		logger.debug(u'message_type: {0}'.format(repr(version)))

		if version is None or \
			message_id is None or \
			firmware is None or \
			controller_id is None or \
			signature is None:
			reason = u'required version(int), message_id(int), firmware(int), controller_id(int), signature(int).'
			logger.debug(reason)
			self.finish( json.dumps({'success': False, 'reason': reason}) )
			return

		try:
			version = int(version)
			message_id = int(message_id)
			firmware = int(firmware)
			controller_id = int(controller_id)
			signature = int(signature)
		except:
			reason = u'Exception conversion from unicode string to integer.'
			logger.debug(reason)
			self.finish( json.dumps({'success': False, 'reason': reason}) )
			return

		d = yield gen.Task(self.post_pool, version, message_type, message_id, firmware, controller_id, signature)
		self.finish( json.dumps({'success': d['success'], 'reason': d['reason']}) )

	def post_pool(self, version, message_type, message_id, firmware, controller_id, signature, callback):

		length = self.get_length(version, message_type, message_id, firmware, controller_id)

		# header ---------------------------------
		header = self.START+\
			length+\
			self.get_version(version)+\
			message_type+\
			self.get_message_id(message_id)+\
			self.get_firmware(firmware)+\
			self.get_controller_id(controller_id)

		# payload --------------------------------

		zeros = '\x00' * 15
		# signature = 1
		payload = \
			zeros+\
			self.hex_to_byte(self.int_to_hex(signature))

		# -----------------------------------------------

		logger.debug( 30 * u'-' )
		logger.debug(u'header: {0}'.format(repr(header)))
		logger.debug(u'header length: {0}'.format(len(header)))
		logger.debug( 30 * u'-' )
		logger.debug(u'payload before aes: {0}'.format(repr(payload)))
		logger.debug(u'payload length: {0}'.format(len(payload)))
		logger.debug( 30 * u'-' )

		# aes encryption
		payload = self.aes_encrypt(payload)
		payload = payload.replace('\n', '\x0D') # Check.
		logger.debug(u'payload after aes: {0}'.format(repr(payload)))
		logger.debug(u'payload length: {0}'.format(len(payload)))
		logger.debug( 30 * u'-' )

		# create crc8
		cmd = header+payload
		crc8_byte = self.create_crc8_val(cmd)
		fire_gps_starting_up = cmd+crc8_byte

		logger.debug(u'fire_gps_starting_up: {0}'.format(repr(fire_gps_starting_up)))
		logger.debug(u'fire_gps_starting_up length: {0}'.format(len(fire_gps_starting_up)))
		logger.debug( 30 * u'-' )

		if not self.crc8_verification(fire_gps_starting_up):
			reason = u'CRC8 verification error before sending fire_gps_starting_up message. Exit!'
			logger.debug(reason)
			d = {'success': False, 'reason': reason}
			return callback(d)

		# sending socket.


class BleKeyUpdate(BaseHandler):
	'''Initiate sending ble_key_update message.'''

	@web.asynchronous
	@gen.engine
	@access_token
	def post(self, *args, **kwargs):
		payload = json.loads(self.request.body)

		version = payload.get('version', None)
		message_id = payload.get('message_id', None)
		firmware = payload.get('firmware', None)
		controller_id = payload.get('controller_id', None)
		ble_key1 = payload.get('ble_key1', None) # int, 19 digit
		ble_key2 = payload.get('ble_key2', None) # int, 19 digit
		signature = payload.get('signature', None)

		if version == '': version = None
		if message_id == '': message_id = None
		if firmware == '': firmware = None
		if controller_id == '': controller_id = None
		if ble_key1 == '': ble_key1 = None
		if ble_key2 == '': ble_key2 = None
		if signature == '': signature = None

		message_type = self.SERVER_TYPE['ble_key_update']

		logger.debug( 30 * u'-' )
		logger.debug(u'Post ble_key_update:')
		logger.debug(u'version: {0}'.format(version))
		logger.debug(u'message_id: {0}'.format(message_id))
		logger.debug(u'firmware: {0}'.format(firmware))
		logger.debug(u'controller_id: {0}'.format(controller_id))
		logger.debug(u'ble_key1: {0}'.format(ble_key1))
		logger.debug(u'ble_key2: {0}'.format(ble_key2))
		logger.debug(u'signature: {0}'.format(signature))
		logger.debug(u'message_type: {0}'.format(repr(version)))

		if version is None or \
			message_id is None or \
			firmware is None or \
			controller_id is None or \
			ble_key1 is None or \
			ble_key2 is None or \
			signature is None:
			reason = u'required version(int), message_id(int), firmware(int), controller_id(int), ble_key1(int), ble_key2(int), signature(int).'
			logger.debug(reason)
			self.finish( json.dumps({'success': False, 'reason': reason}) )
			return

		if len(ble_key1) <> 19 or len(ble_key2) <> 19:
			reason = u'length of ble_key1 or ble_key2 is not correct.'
			logger.debug(reason)
			self.finish( json.dumps({'success': False, 'reason': reason}) )
			return

		try:
			version = int(version)
			message_id = int(message_id)
			firmware = int(firmware)
			controller_id = int(controller_id)
			ble_key1 = int(ble_key1)
			ble_key2 = int(ble_key2)
			signature = int(signature)
		except:
			reason = u'Exception conversion from unicode string to integer.'
			logger.debug(reason)
			self.finish( json.dumps({'success': False, 'reason': reason}) )
			return

		d = yield gen.Task(self.post_pool, version, message_type, message_id, firmware, controller_id, ble_key1, ble_key2, signature)
		self.finish( json.dumps({'success': d['success'], 'reason': d['reason']}) )

	def post_pool(self, version, message_type, message_id, firmware, controller_id, ble_key1, ble_key2, signature, callback):

		length = self.get_length(version, message_type, message_id, firmware, controller_id)

		# header ---------------------------------
		header = self.START+\
			length+\
			self.get_version(version)+\
			message_type+\
			self.get_message_id(message_id)+\
			self.get_firmware(firmware)+\
			self.get_controller_id(controller_id)

		# payload --------------------------------

		zeros1 = '\x00' * 8
		zeros2 = '\x00' * 7
		# signature = 1
		payload = \
			self.hex_to_byte(self.int_to_hex(ble_key1))+\
			self.hex_to_byte(self.int_to_hex(ble_key2))+\
			zeros1+\
			zeros2+\
			self.hex_to_byte(self.int_to_hex(signature))

		# -----------------------------------------------

		logger.debug( 30 * u'-' )
		logger.debug(u'header: {0}'.format(repr(header)))
		logger.debug(u'header length: {0}'.format(len(header)))
		logger.debug( 30 * u'-' )
		logger.debug(u'payload before aes: {0}'.format(repr(payload)))
		logger.debug(u'payload length: {0}'.format(len(payload)))
		logger.debug( 30 * u'-' )

		# aes encryption
		payload = self.aes_encrypt(payload)
		payload = payload.replace('\n', '\x0D') # Check.
		logger.debug(u'payload after aes: {0}'.format(repr(payload)))
		logger.debug(u'payload length: {0}'.format(len(payload)))
		logger.debug( 30 * u'-' )

		# create crc8
		cmd = header+payload
		crc8_byte = self.create_crc8_val(cmd)
		ble_key = cmd+crc8_byte

		logger.debug(u'ble_key: {0}'.format(repr(ble_key)))
		logger.debug(u'ble_key length: {0}'.format(len(ble_key)))
		logger.debug( 30 * u'-' )

		if not self.crc8_verification(ble_key):
			reason = u'CRC8 verification error before sending ble_key message. Exit!'
			logger.debug(reason)
			d = {'success': False, 'reason': reason}
			return callback(d)

		# sending socket.
