# coding: utf-8
# @2017
# Fauzi, fauziwei@yahoo.com
import os
import sys
import logging
import binascii
import traceback
from Crypto.Cipher import AES
from sqlalchemy.exc import IntegrityError

# local import
from header import START, CLIENT_TYPE, SERVER_TYPE
from utils import *
# from models import Db, Client, User, \
# 	Status, StatusRecord, InformationRecord, \
# 	GpsRecord, AbnormalRecord, BleKeyRecord

from models import Db, Client, User, \
	Status, GpsRecord, BleKeyRecord, \
	ConfigurationRecord

reload(sys)
sys.setdefaultencoding('utf-8')

logger = logging.getLogger(__name__)


class Logic(object):

	def parsing_crc8(self, proto, data):
		'''Cut recv_data.
		Data is supposed in ByteStream.
		Default is todo decryption after checking CRC8, ...
		unless 'hearbeat' and 'normal_ack' message.
		'''
		if not crc8_verification(data):
			logger.debug(u'CRC8 verification failed.')
			return

		start = data[0]
		length = data[1:3]
		version = data[3]
		message_type = data[4]
		message_id = data[5:7]
		firmware = data[7]
		device_id = data[8:16]
		crc = data[-1:]

		logger.debug( 30 * u'-')
		logger.debug(u'Received...')

		logger.debug(u'start: {0}'.format(repr(start)))
		logger.debug(u'header length: {0} bytes'.format(hex_to_int(byte_to_hex(length))))
		logger.debug(u'version: {0}'.format(repr(version)))
		logger.debug(u'message_type: {0}'.format(repr(message_type)))
		logger.debug(u'message_id: {0}'.format(repr(message_id)))
		logger.debug(u'firmware: {0}'.format(repr(firmware)))
		logger.debug(u'device_id: {0}'.format(hex_to_int(byte_to_hex(device_id))))

		if message_type in [ CLIENT_TYPE['heartbeat'], CLIENT_TYPE['normal_ack'] ]:
			logger.debug(u'crc: {0}'.format(repr(crc)))
			return {
				'start': start, 'length': length, 'version': version,
				'message_type': message_type, 'message_id': message_id,
				'firmware': firmware, 'device_id': device_id
			}

		payload = data[16:-1]
		payload = self.aes_decrypt(proto, payload) # data is minus crc
		logger.debug(u'payload: {0}'.format(repr(payload)))
		logger.debug(u'crc: {0}'.format(repr(crc)))

		logger.debug( 30 * u'-')

		return {
			'start': start, 'length': length, 'version': version,
			'message_type': message_type, 'message_id': message_id,
			'firmware': firmware, 'device_id': device_id, 'payload': payload
		}

	def aes_encrypt(self, proto, data):
		'''data is without crc. Only 16bytes.'''
		IV = os.urandom(16)
		aes = AES.new(proto.factory.aes_key, AES.MODE_ECB, IV=IV)
		return aes.encrypt(data)

	def aes_decrypt(self, proto, data):
		'''data is without crc. Only 16bytes.'''
		IV = os.urandom(16)
		aes = AES.new(proto.factory.aes_key, AES.MODE_ECB, IV=IV)
		return aes.decrypt(data)


	''' Sending section. '''

	def unlock_processing(self, data):
		'''Relaying data from controller to device.'''
		return data

	def lock_processing(self, data):
		'''Relaying data from controller to device.'''
		return data

	def fire_gps_starting_up_processing(self, data):
		'''Relaying data from controller to device.'''
		return data

	def ble_key_update_processing(self, data):
		'''Relaying data from controller to device.'''
		return data


	''' Receiving section. '''

	def heartbeat_processing(self, proto, parsed):
		'''Preparing response *normal_ack* to device.'''
		length = parsed['length']
		message_type = SERVER_TYPE['normal_ack']

		# message_id += 1
		message_id = parsed['message_id']
		message_id = hex_to_int(byte_to_hex(message_id)) + 1
		message_id = hex_to_byte(int_to_hex(message_id))

		device_id = parsed['device_id']
		version = parsed['version']
		firmware = parsed['firmware']
		
		# header
		header = START+length+version+message_type+message_id+firmware+device_id
		
		# payload ---------------------------------
		# timestamp (4bytes)
		t = get_shanghai_time()
		timestamp = to_timestamp(t)
		timestamp = timestamp_to_byte(timestamp)
		payload = timestamp

		# normal_ack doesnt required to be encrypted.
		cmd = header+payload
		crc8_byte = create_crc8_val(cmd)
		normal_ack = cmd+crc8_byte

		logger.debug(u'Prepare response normal_ack:')
		logger.debug(u'normal_ack: {0}'.format(repr(normal_ack)))
		# logger.debug(u'normal_ack: {0}'.format(ascii_string(normal_ack)))
		logger.debug(u'Length of normal_ack: {0}'.format(len(normal_ack)))

		if not crc8_verification(normal_ack):
			logger.debug(u'Error CRC8 normal_ack, send feedback fails.')
			return
		return normal_ack

	def normal_ack_processing(self, proto, parsed):
		'''Relaying data from device to controller.
		1st reply fire_gps_starting_up.
		'''

	def lock_unlock_response_processing(self, proto, parsed):
		'''Relaying data from device to controller.
		Device inform its new status, this twisted relay 'success' to controller.
		'''
		# length = parsed['length']
		# message_type = parsed['message_type']
		# Server should update device status here, by saving to database.
		# message_id = parsed['message_id'] # Check the status.
		# device_id = parsed['device_id']
		# version = parsed['version']
		# firmware = parsed['firmware']

	def gps_data_report_processing(self, proto, parsed):
		'''Preparing relaying gps_data_report from device to controller.'''
		# length = parsed['length']
		# message_type = parsed['message_type']
		# message_id = parsed['message_id']
		# device_id = parsed['device_id']
		# version = parsed['version']
		# firmware = parsed['firmware']

	def normal_bike_status_processing(self, proto, parsed):
		'''Preparing response normal_ack to device.'''
		length = parsed['length']
		message_type = SERVER_TYPE['normal_ack']

		# message_id += 1
		message_id = parsed['message_id']
		message_id = hex_to_int(byte_to_hex(message_id)) + 1
		message_id = hex_to_byte(int_to_hex(message_id))

		device_id = parsed['device_id']
		version = parsed['version']
		firmware = parsed['firmware']

		# Cutting received payload 'normal_bike_status'
		payload = parsed['payload']

		# header
		header = START+length+version+message_type+message_id+firmware+device_id

		# payload ---------------------------------
		# timestamp (4bytes)
		t = get_shanghai_time()
		timestamp = to_timestamp(t)
		timestamp = timestamp_to_byte(timestamp)
		payload = timestamp

		# normal_ack doesnt required to be encrypted.
		cmd = header+payload
		crc8_byte = create_crc8_val(cmd)
		normal_ack = cmd+crc8_byte

		logger.debug(u'Prepare response normal_ack:')
		logger.debug(u'normal_ack: {0}'.format(repr(normal_ack)))
		# logger.debug(u'normal_ack: {0}'.format(ascii_string(normal_ack)))
		logger.debug(u'Length of normal_ack: {0}'.format(len(normal_ack)))

		if not crc8_verification(normal_ack):
			logger.debug(u'Error CRC8 normal_ack, send feedback fails.')
			return
		return normal_ack

	def pedelec_status_report_processing(self, proto, parsed):
		'''Preparing response normal_ack to device.'''
		length = parsed['length']
		message_type = SERVER_TYPE['normal_ack']

		# message_id += 1
		message_id = parsed['message_id']
		message_id = hex_to_int(byte_to_hex(message_id)) + 1
		message_id = hex_to_byte(int_to_hex(message_id))

		device_id = parsed['device_id']
		version = parsed['version']
		firmware = parsed['firmware']

		# Cutting received payload 'pedelec_status_report'
		payload = parsed['payload']

		# header
		header = START+length+version+message_type+message_id+firmware+device_id

		# payload ---------------------------------
		# timestamp (4bytes)
		t = get_shanghai_time()
		timestamp = to_timestamp(t)
		timestamp = timestamp_to_byte(timestamp)
		payload = timestamp

		# normal_ack doesnt required to be encrypted.
		cmd = header+payload
		crc8_byte = create_crc8_val(cmd)
		normal_ack = cmd+crc8_byte

		logger.debug(u'Prepare response normal_ack:')
		logger.debug(u'normal_ack: {0}'.format(repr(normal_ack)))
		# logger.debug(u'normal_ack: {0}'.format(ascii_string(normal_ack)))
		logger.debug(u'Length of normal_ack: {0}'.format(len(normal_ack)))

		if not crc8_verification(normal_ack):
			logger.debug(u'Error CRC8 normal_ack, send feedback fails.')
			return
		return normal_ack

	def fault_report_processing(self, proto, parsed):
		'''Preparing response normal_ack to device.'''
		length = parsed['length']
		message_type = SERVER_TYPE['normal_ack']

		# message_id += 1
		message_id = parsed['message_id']
		message_id = hex_to_int(byte_to_hex(message_id)) + 1
		message_id = hex_to_byte(int_to_hex(message_id))

		device_id = parsed['device_id']
		version = parsed['version']
		firmware = parsed['firmware']

		# Cutting received payload 'fault_report'
		payload = parsed['payload']

		# header
		header = START+length+version+message_type+message_id+firmware+device_id

		# payload ---------------------------------
		# timestamp (4bytes)
		t = get_shanghai_time()
		timestamp = to_timestamp(t)
		timestamp = timestamp_to_byte(timestamp)
		payload = timestamp

		# normal_ack doesnt required to be encrypted.
		cmd = header+payload
		crc8_byte = create_crc8_val(cmd)
		normal_ack = cmd+crc8_byte

		logger.debug(u'Prepare response normal_ack:')
		logger.debug(u'normal_ack: {0}'.format(repr(normal_ack)))
		# logger.debug(u'normal_ack: {0}'.format(ascii_string(normal_ack)))
		logger.debug(u'Length of normal_ack: {0}'.format(len(normal_ack)))

		if not crc8_verification(normal_ack):
			logger.debug(u'Error CRC8 normal_ack, send feedback fails.')
			return
		return normal_ack		

	def ble_key_response_processing(self, proto, parsed):
		'''Relaying data from device to controller.'''

	def command_response_processing(self, proto, parsed):
		pass

	def upgrade_push_response_processing(self, proto, parsed):
		pass

	def upgrade_data_request_processing(self, proto, parsed):
		pass

	def setting(self, proto, data):
		'''proto is parent's self.
		The incoming data is from controller.
		'''
		parsed = self.parsing_crc8(proto, data)
		if not parsed:

	def communication(self, proto, data):
		'''proto is parent's self.
		The incoming data is from device.
		'''
		parsed = self.parsing_crc8(proto, data)
		if not parsed:
			return

		return
