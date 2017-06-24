# coding: utf-8
# @2017
# Fauzi, fauziwei@yahoo.com
import os
import sys
import logging
import binascii
from Crypto.Cipher import AES

# local import
from header import START, CLIENT_TYPE, SERVER_TYPE
from utils import byte_to_hex, hex_to_int, ascii_string, \
	crc8_verification, create_crc8_val
from models import Db, commit, Device

reload(sys)
sys.setdefaultencoding('utf-8')

logger = logging.getLogger(__name__)


class Logic(object):

	def parsing_crc8(self, proto, data):
		'''Cut recv_data.
		Data is supposed in ByteStream with length 17bytes
		default is todo encryption after checking CRC8, otherwise do decryption
		'''
		if len(data) <> 17:
			logger.debug(u'Parsing 17bytes failed.')
			return

		if not crc8_verification(data):
			logger.debug(u'CRC8 verification failed.')
			return

		logger.debug( 30 * u'-')
		logger.debug(u'Real data before encrypt/decrypt.')

		start = data[0]
		length = data[1:3]
		version = data[3]
		message_type = data[4]
		message_id = data[5:7]
		firmware = data[7]
		device_id = data[8:-1]
		crc = data[-1:]

		logger.debug(u'start: {0}'.format(repr(start)))
		logger.debug(u'length: {0} bytes'.format(hex_to_int(byte_to_hex(length))))
		logger.debug(u'version: {0}'.format(repr(version)))
		logger.debug(u'message_type: {0}'.format(repr(message_type)))
		logger.debug(u'message_id: {0}'.format(repr(message_id)))
		logger.debug(u'firmware: {0}'.format(repr(firmware)))
		logger.debug(u'device_id: {0}'.format(byte_to_hex(device_id)))
		logger.debug(u'crc: {0}'.format(repr(crc)))

		if message_type == CLIENT_TYPE['heartbeat'] or \
			message_type == CLIENT_TYPE['normal_bike_status']:
			logger.debug(u'Detected message_type which doesnt required to be encrypted or decrypted.')
			return {
				'start': start, 'length': length, 'version': version,
				'message_type': message_type, 'message_id': message_id,
				'firmware': firmware, 'device_id': device_id
			}

		logger.debug( 30 * u'-')

		logger.debug(u'Data after decrypted.')
		data = self.aes_decrypt(proto, data[:-1]) # data is minus crc

		start = data[0]
		length = data[1:3]
		version = data[3]
		message_type = data[4]
		message_id = data[5:7]
		firmware = data[7]
		device_id = data[8:]

		logger.debug(u'start: {0}'.format(repr(start)))
		logger.debug(u'length: {0} bytes'.format(hex_to_int(byte_to_hex(length))))
		logger.debug(u'version: {0}'.format(repr(version)))
		logger.debug(u'message_type: {0}'.format(repr(message_type)))
		logger.debug(u'message_id: {0}'.format(repr(message_id)))
		logger.debug(u'firmware: {0}'.format(repr(firmware)))
		logger.debug(u'device_id: {0}'.format(byte_to_hex(device_id)))

		logger.debug( 30 * u'-')

		return {
			'start': start, 'length': length, 'version': version,
			'message_type': message_type, 'message_id': message_id,
			'firmware': firmware, 'device_id': device_id
		}

	def aes_encrypt(self, proto, data):
		'''data is without crc. Only 16bytes.'''
		IV = os.urandom(16)
		# logger.debug(u'IV: {0}'.format(binascii.hexlify(IV).upper()))
		aes = AES.new(proto.factory.aes_key, AES.MODE_ECB, IV=IV)
		ciphertext = aes.encrypt(data)
		logger.debug(u'cyphertext: {0}'.format(repr(ciphertext)))
		return ciphertext

	def aes_decrypt(self, proto, data):
		'''data is without crc. Only 16bytes.'''
		IV = os.urandom(16)
		aes = AES.new(proto.factory.aes_key, AES.MODE_ECB, IV=IV)
		text = aes.decrypt(data)
		return text


	''' Sending section. '''

	def unlock_processing(self, proto, parsed):
		'''Relaying data from controller to device.'''
		length = parsed['length']
		message_type = SERVER_TYPE['unlock']
		message_id = parsed['message_id'] # Check, it required tobe modified.
		device_id = parsed['device_id']
		version = parsed['version']
		firmware = parsed['firmware']

		cmd = START+length+version+message_type+message_id+firmware+device_id
		# aes encryption
		cmd = self.aes_encrypt(proto, cmd)
		# create crc8
		crc8_byte = create_crc8_val(cmd)
		unlock = cmd+crc8_byte

		logger.debug(u'Preparing relay unlock from controller to device:')
		logger.debug(u'unlock: {0}'.format(repr(unlock)))
		# logger.debug(u'unlock: {0}'.format(ascii_string(unlock)))
		logger.debug(u'Length of unlock: {0}'.format(len(unlock)))

		crc8_verification(unlock)
		return unlock

	def lock_processing(self, proto, parsed):
		'''Relaying data from controller to device.'''
		length = parsed['length']
		message_type = SERVER_TYPE['lock']
		message_id = parsed['message_id'] # Check, it required tobe modified.
		device_id = parsed['device_id']
		version = parsed['version']
		firmware = parsed['firmware']

		cmd = START+length+version+message_type+message_id+firmware+device_id
		# aes encryption
		cmd = self.aes_encrypt(proto, cmd)
		# create crc8
		crc8_byte = create_crc8_val(cmd)
		lock = cmd+crc8_byte

		logger.debug(u'Preparing relay lock from controller to device:')
		logger.debug(u'lock: {0}'.format(repr(lock)))
		# logger.debug(u'lock: {0}'.format(ascii_string(lock)))
		logger.debug(u'Length of lock: {0}'.format(len(lock)))

		crc8_verification(lock)
		return lock


	''' Receiving section. '''

	def heartbeat_processing(self, proto, parsed):
		'''Preparing response to device.'''
		length = parsed['length']
		message_type = SERVER_TYPE['normal_ack']
		message_id = parsed['message_id']
		device_id = parsed['device_id']
		version = parsed['version']
		firmware = parsed['firmware']
		# has timestamp
		cmd = START+length+version+message_type+message_id+firmware+device_id
		# normal_ack doesnt required to be encrypted.
		crc8_byte = create_crc8_val(cmd)
		normal_ack = cmd+crc8_byte

		logger.debug(u'Prepare response normal_ack:')
		logger.debug(u'normal_ack: {0}'.format(repr(normal_ack)))
		# logger.debug(u'normal_ack: {0}'.format(ascii_string(normal_ack)))
		logger.debug(u'Length of normal_ack: {0}'.format(len(normal_ack)))

		crc8_verification(normal_ack)
		return normal_ack

	def lock_unlock_response_processing(self, proto, parsed):
		'''Relaying data from device to controller.
		Device inform its new status, this twisted relay 'success' to controller.
		'''
		length = parsed['length']
		message_type = parsed['message_type']
		# Server should update device status here, by saving to database.
		message_id = parsed['message_id'] # Check the status.
		device_id = parsed['device_id']
		version = parsed['version']
		firmware = parsed['firmware']

		# Store to database based on 'lock' or 'unlock' status.

		# Send message 'success' to controller.
		if proto.device_id not in proto.factory.controllers:
			logger.debug(u'controller_id {0} is not connected.'.format(proto.device_id))
			return

		logger.debug(u'Prepare for relaying data to controller_id: {0}'.format(proto.device_id))
		proto.belongto_controller = proto.factory.controllers[proto.device_id]
		logger.debug(u'Send response success: {0}'.format(repr(proto.response_success)))
		proto.belongto_controller.sendLine(proto.response_success)
		proto.belongto_controller = False
		return

	def gps_data_report_processing(self, proto, parsed):
		pass

	def normal_bike_status_processing(self, proto, parsed):
		'''Preparing response to device.'''
		length = parsed['length']
		message_type = SERVER_TYPE['normal_ack']
		message_id = parsed['message_id']
		device_id = parsed['device_id']
		version = parsed['version']
		firmware = parsed['firmware']
		# has timestamp
		cmd = START+length+version+message_type+message_id+firmware+device_id
		# normal_ack doesnt required to be encrypted.
		crc8_byte = create_crc8_val(cmd)
		normal_ack = cmd+crc8_byte

		logger.debug(u'Prepare response normal_ack:')
		logger.debug(u'normal_ack: {0}'.format(repr(normal_ack)))
		# logger.debug(u'normal_ack: {0}'.format(ascii_string(normal_ack)))
		logger.debug(u'Length of normal_ack: {0}'.format(len(normal_ack)))

		crc8_verification(normal_ack)
		return normal_ack

	def pedelec_status_report_processing(self, proto, parsed):
		pass

	def fault_report_processing(self, proto, parsed):
		pass

	def ble_key_response_processing(self, proto, parsed):
		pass

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
			return

		proto.controller_id = byte_to_hex(parsed['device_id'])

		if proto.controller_id not in proto.factory.devices:
			logger.debug(u'device_id {0} is not connected.'.format(proto.controller_id))
			return

		logger.debug(u'Prepare for relaying data to device_id: {0}'.format(proto.controller_id))
		proto.belongto_device = proto.factory.devices[proto.controller_id]

		# Store connected controller to self.controllers.
		proto.factory.controllers[proto.controller_id] = proto

		# Store connected controller to redis.
		proto.factory.controllers_cache.set(proto.controller_id, '{0}:{1}'.format(proto.factory.server_ip, proto.factory.server_port))
		proto.token_controller = True

		if parsed['message_type'] == SERVER_TYPE['unlock']:
			return self.unlock_processing(proto, parsed)

		elif parsed['message_type'] == SERVER_TYPE['lock']:
			return self.lock_processing(proto, parsed)

		else:
			# Still several message_type unfinished yet.
			pass

		return


	def communication(self, proto, data):
		'''proto is parent's self.
		The incoming data is from device.
		'''
		parsed = self.parsing_crc8(proto, data)
		if not parsed:
			return

		proto.device_id = byte_to_hex(parsed['device_id'])

		# Store connected device to self.devices
		proto.factory.devices[proto.device_id] = proto

		# Store connected device to redis, later, it will be accessed by its controller.
		# The controler will search this 'key': proto.device_id in redis,
		# and then get value of ipaddr:port to determine, in which twisted server the device is connected.
		# and then controler can login to the certain twisted server.
		proto.factory.devices_cache.set(proto.device_id, '{0}:{1}'.format(proto.factory.server_ip, proto.factory.server_port))
		proto.token_device = True

		if parsed['message_type'] == CLIENT_TYPE['heartbeat']:
			logger.debug(u'Detected heartbeat...')
			return self.heartbeat_processing(proto, parsed)

		elif parsed['message_type'] == CLIENT_TYPE['lock_unlock_response']:
			logger.debug(u'Detected lock_unlock_response...')
			return self.lock_unlock_response_processing(proto, parsed)

		elif parsed['message_type'] ==  CLIENT_TYPE['gps_data_report']:
			logger.debug(u'Detected gps_data_report...')
			return self.gps_data_report_processing(proto, parsed)

		elif parsed['message_type'] ==  CLIENT_TYPE['normal_bike_status']:
			logger.debug(u'Detected normal_bike_status...')
			return self.normal_bike_status_processing(proto, parsed)

		elif parsed['message_type'] ==  CLIENT_TYPE['pedelec_status_report']:
			logger.debug(u'pedelec_status_report...')
			return self.pedelec_status_report_processing(proto, parsed)

		elif parsed['message_type'] ==  CLIENT_TYPE['fault_report']:
			logger.debug(u'Detected fault_report...')
			return self.fault_report_processing(proto, parsed)

		elif parsed['message_type'] ==  CLIENT_TYPE['ble_key_response']:
			logger.debug(u'Detected ble_key_response...')
			return self.ble_key_response_processing(proto, parsed)

		elif parsed['message_type'] ==  CLIENT_TYPE['command_response']:
			logger.debug(u'Detected command_response...')
			return self.command_response_processing(proto, parsed)

		elif parsed['message_type'] ==  CLIENT_TYPE['upgrade_push_response']:
			logger.debug(u'Detected upgrade_push_response...')
			return self.upgrade_push_response_processing(proto, parsed)

		elif parsed['message_type'] ==  CLIENT_TYPE['upgrade_data_request']:
			logger.debug(u'Detected upgrade_data_request...')
			return self.upgrade_data_request_processing(proto, parsed)

		else:
			logger.debug(u'Client Type is not correct. Drop connection.')
			proto.transport.loseConnection()

		return
