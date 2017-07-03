# coding: utf-8
# @2017
# Fauzi, fauziwei@yahoo.com
import sys
import json
import logging
import datetime
from tornado import gen, web
# local import
from base.handlers import BaseHandler
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
		logger.debug(u'Post UnLock:')
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
			self.int_to_byte(signature)

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

		# sending socket.


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
		logger.debug(u'Post Lock:')
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
			self.int_to_byte(signature)

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
		pass


class BleKeyUpdate(BaseHandler):
	'''Initiate sending ble_key_update message.'''

	@web.asynchronous
	@gen.engine
	@access_token
	def post(self, *args, **kwargs):
		pass
