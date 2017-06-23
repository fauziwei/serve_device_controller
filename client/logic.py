# coding: utf-8
# @2017
# Fauzi, fauziwei@yahoo.com
import os
import sys
import logging
import binascii
from Crypto.Cipher import AES

# local import
from header import *
from utils import *

reload(sys)
sys.setdefaultencoding('utf-8')

logger = logging.getLogger(__name__)

def get_version():
	'''Integer to ByteStream.'''
	version = 3
	version = binascii.unhexlify(int_to_hex(version))
	logger.debug(u'version: {0}'.format(repr(version))) # '\x03'
	return version

def get_message_id_for_crc8(message_id):
	'''Integer to ByteStream.
	It supposed to be increased by one
	'''
	# message_id in byte.
	message_id = binascii.unhexlify(int_to_hex(message_id))
	logger.debug(u'message_id in byte: {0}'.format(repr(message_id))) # '\x16'
	# message_id in hex.
	message_id_in_hex = binascii.hexlify(message_id)
	logger.debug(u'message_id in hex: {0}'.format(message_id_in_hex))
	# message_id in int. (back to int)
	message_id_in_int = hex_to_int(message_id_in_hex)
	logger.debug(u'message_id in int: {0}'.format(message_id_in_int))
	return message_id

def get_firmware():
	'''Integer to ByteStream.'''
	firmware = 1
	firmware = binascii.unhexlify(int_to_hex(firmware))
	logger.debug(u'firmware: {0}'.format(repr(firmware))) # '\x01'
	return firmware

def get_length_for_crc8(message_type, message_id, device_id):
	length = len(START)+2+len(get_version())+len(message_type)+\
		len(message_id)+len(get_firmware())+len(device_id)+1
	logger.debug(u'length of total message: {0}'.format(length))
	return convert_length_to_byte(length)


class Logic(object):

	def parsing_crc8(self, proto, data):
		'''Cut recv_data.
		Data is supposed in ByteStream with length 17bytes
		default is todo encryption after checking CRC8, otherwise do decryption
		'''
		if len(data) <> 17:
			logger.debug(u'Parsing data 17bytes failed.')
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
		# crc = data[-1:]

		logger.debug(u'start: {0}'.format(repr(start)))
		logger.debug(u'length: {0} bytes'.format(hex_to_int(byte_to_hex(length))))
		logger.debug(u'version: {0}'.format(repr(version)))
		logger.debug(u'message_type: {0}'.format(repr(message_type)))
		logger.debug(u'message_id: {0}'.format(repr(message_id)))
		logger.debug(u'firmware: {0}'.format(repr(firmware)))
		logger.debug(u'device_id: {0}'.format(byte_to_hex(device_id)))
		# logger.debug(u'crc: {0}'.format(repr(crc)))

		'''Ask to laoban wheter normal_ack is encrypted?.'''
		if message_type == SERVER_TYPE['normal_ack']:
			logger.debug(u'Detected normal_ack message_type, doesnt required to be encrypted or decrypted.')
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
		# crc = data[-1:]

		logger.debug(u'start: {0}'.format(repr(start)))
		logger.debug(u'length: {0} bytes'.format(hex_to_int(byte_to_hex(length))))
		logger.debug(u'version: {0}'.format(repr(version)))
		logger.debug(u'message_type: {0}'.format(repr(message_type)))
		logger.debug(u'message_id: {0}'.format(repr(message_id)))
		logger.debug(u'firmware: {0}'.format(repr(firmware)))
		logger.debug(u'device_id: {0}'.format(byte_to_hex(device_id)))
		# logger.debug(u'crc: {0}'.format(repr(crc)))

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
		aes = AES.new(proto.aes_key, AES.MODE_ECB, IV=IV)
		ciphertext = aes.encrypt(data)
		logger.debug(u'cyphertext: {0}'.format(repr(ciphertext)))
		return ciphertext

	def aes_decrypt(self, proto, data):
		'''data is without crc. Only 16bytes.'''
		IV = os.urandom(16)
		aes = AES.new(proto.aes_key, AES.MODE_ECB, IV=IV)
		text = aes.decrypt(data)
		return text


	''' Sending section. '''

	def init_heartbeat(self, proto):
		'''Sample initiator heartbeat to server.'''
		message_type = CLIENT_TYPE['heartbeat']
		message_id = get_message_id_for_crc8(proto.message_id)
		# device_id = uni_to_byte(proto.device_id)
		device_id = hex_to_byte(proto.device_id)
		length = get_length_for_crc8(message_type, message_id, device_id)
		version = get_version()
		firmware = get_firmware()

		cmd = START+length+version+message_type+message_id+firmware+device_id
		# aes encryption, heartbeat doesnt required tobe encrypted.
		# cmd = self.aes_encrypt(proto, cmd)
		# create crc8
		crc8_byte = create_crc8_val(cmd)
		heartbeat = cmd+crc8_byte

		logger.debug(u'heartbeat: {0}'.format(repr(heartbeat)))
		logger.debug(u'heartbeat: {0}'.format(ascii_string(heartbeat)))
		logger.debug(u'Length of heartbeat: {0}'.format(len(heartbeat)))

		crc8_verification(heartbeat)
		proto.token_init_heartbeat = True
		return heartbeat


	''' Receiving section. '''

	def normal_ack_processing(self, proto, parsed):
		'''Nothing todo.'''
		return

	def unlock_processing(self, proto, parsed):
		'''Preparing send to server.'''
		length = parsed['length']
		message_type = CLIENT_TYPE['lock_unlock_response']
		message_id = parsed['message_id'] # Check, it required tobe modified.
		device_id = parsed['device_id']
		version = parsed['version']
		firmware = parsed['firmware']		

		cmd = START+length+version+message_type+message_id+firmware+device_id
		# aes encryption
		cmd = self.aes_encrypt(proto, cmd)
		# create crc8
		crc8_byte = create_crc8_val(cmd)
		lock_unlock_response = cmd+crc8_byte

		logger.debug(u'Preparing relay lock_unlock_response from device to controller:')
		logger.debug(u'lock_unlock_response: {0}'.format(repr(lock_unlock_response)))
		logger.debug(u'lock_unlock_response: {0}'.format(ascii_string(lock_unlock_response)))
		logger.debug(u'Length of lock_unlock_response: {0}'.format(len(lock_unlock_response)))

		crc8_verification(lock_unlock_response)
		return lock_unlock_response

	def lock_processing(self, proto, parsed):
		'''Preparing send to server.'''
		length = parsed['length']
		message_type = CLIENT_TYPE['lock_unlock_response']
		message_id = parsed['message_id'] # Check, it required tobe modified.
		device_id = parsed['device_id']
		version = parsed['version']
		firmware = parsed['firmware']		

		cmd = START+length+version+message_type+message_id+firmware+device_id
		# aes encryption
		cmd = self.aes_encrypt(proto, cmd)
		# create crc8
		crc8_byte = create_crc8_val(cmd)
		lock_unlock_response = cmd+crc8_byte

		logger.debug(u'Preparing relay lock_unlock_response from device to controller:')
		logger.debug(u'lock_unlock_response: {0}'.format(repr(lock_unlock_response)))
		logger.debug(u'lock_unlock_response: {0}'.format(ascii_string(lock_unlock_response)))
		logger.debug(u'Length of lock_unlock_response: {0}'.format(len(lock_unlock_response)))

		crc8_verification(lock_unlock_response)
		return lock_unlock_response

	def configuration_command_processing(self, proto, parsed):
		pass

	def fire_gps_starting_up_processing(self, proto, parsed):
		pass

	def get_device_status_processing(self, proto, parsed):
		pass

	def ble_key_update_processing(self, proto, parsed):
		pass

	def control_command_send_processing(self, proto, parsed):
		pass

	def upgrade_command_push_processing(self, proto, parsed):
		pass

	def upgrade_data_send_processing(self, proto, parsed):
		pass

	def communication(self, proto, data):

		parsed = self.parsing_crc8(proto, data)
		if not parsed:
			return

		if parsed['message_type'] == SERVER_TYPE['normal_ack']:
			logger.debug(u'Detected normal_ack...')
			return self.normal_ack_processing(proto, parsed)

		elif parsed['message_type'] == SERVER_TYPE['unlock']:
			logger.debug(u'Detected unlock...')
			return self.unlock_processing(proto, parsed)

		elif parsed['message_type'] == SERVER_TYPE['lock']:
			logger.debug(u'Detected lock...')
			return self.lock_processing(proto, parsed)

		elif parsed['message_type'] == SERVER_TYPE['configuration_command']:
			logger.debug(u'Detected configuration_command...')
			return self.configuration_command_processing(proto, parsed)

		elif parsed['message_type'] == SERVER_TYPE['fire_gps_starting_up']:
			logger.debug(u'Detected fire_gps_starting_up...')
			return self.fire_gps_starting_up_processing(proto, parsed)

		elif parsed['message_type'] == SERVER_TYPE['get_device_status']:
			logger.debug(u'Detected get_device_status...')
			return self.get_device_status_processing(proto, parsed)

		elif parsed['message_type'] == SERVER_TYPE['ble_key_update']:
			logger.debug(u'Detected ble_key_update...')
			return self.ble_key_update_processing(proto, parsed)

		elif parsed['message_type'] == SERVER_TYPE['control_command_send']:
			logger.debug(u'Detected control_command_send...')
			return self.control_command_send_processing(proto, parsed)

		elif parsed['message_type'] == SERVER_TYPE['upgrade_command_push']:
			logger.debug(u'Detected upgrade_command_push...')
			return self.upgrade_command_push_processing(proto, parsed)

		elif parsed['message_type'] == SERVER_TYPE['upgrade_data_send']:
			logger.debug(u'Detected upgrade_data_send...')
			return self.upgrade_data_send_processing(proto, parsed)

		else:
			logger.debug(u'Server Type is not correct. Drop connection.')
			proto.transport.loseConnection()

		return
