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
	# message_id_in_hex = binascii.hexlify(message_id)
	# logger.debug(u'message_id in hex: {0}'.format(message_id_in_hex))
	# message_id in int. (back to int)
	# message_id_in_int = hex_to_int(message_id_in_hex)
	# logger.debug(u'message_id in int: {0}'.format(message_id_in_int))
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
		payload = data[16:-1]
		crc = data[-1:]

		logger.debug( 30 * u'-')
		logger.debug('Receiving...')

		logger.debug(u'start: {0}'.format(repr(start)))
		logger.debug(u'length: {0} bytes'.format(hex_to_int(byte_to_hex(length))))
		logger.debug(u'version: {0}'.format(repr(version)))
		logger.debug(u'message_type: {0}'.format(repr(message_type)))
		logger.debug(u'message_id: {0}'.format(repr(message_id)))
		logger.debug(u'firmware: {0}'.format(repr(firmware)))
		logger.debug(u'device_id: {0}'.format(byte_to_hex(device_id)))

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


	''' Sending section.'''

	def init_unlock(self, proto):
		'''Send data to device via twisted server.'''
		message_type = SERVER_TYPE['unlock']
		logger.debug('message_type: {0}'.format(repr(message_type)))
		message_id = get_message_id_for_crc8(proto.message_id)
		controller_id = hex_to_byte(proto.controller_id)
		length = get_length_for_crc8(message_type, message_id, controller_id)
		version = get_version()
		firmware = get_firmware()

		# header
		header = START+length+version+message_type+message_id+firmware+controller_id

		# payload ------------------------------------
		# end_timestamp (4bytes)
		t = get_shanghai_time()
		end_timestamp = to_timestamp(t)
		end_timestamp = timestamp_to_byte(end_timestamp)

		# start_timestamp (4bytes)
		t = get_shanghai_time()
		start_timestamp = to_timestamp(t)
		start_timestamp = timestamp_to_byte(start_timestamp)

		zeros = '\x00' * 7
		signature = 1
		payload = \
			end_timestamp+\
			start_timestamp+\
			zeros+\
			int_to_byte(signature)

		# -----------------------------------------------

		logger.debug(u'payload length: {0}'.format(len(payload)))

		# aes encryption
		payload = self.aes_encrypt(proto, payload)
		# create crc8
		cmd = header+payload
		crc8_byte = create_crc8_val(cmd)
		unlock = cmd+crc8_byte		

		logger.debug(u'unlock: {0}'.format(repr(unlock)))
		# logger.debug(u'unlock: {0}'.format(ascii_string(unlock)))
		logger.debug(u'Length of unlock: {0}'.format(len(unlock)))

		crc8_verification(unlock)
		proto.token_init_unlock = True
		return unlock

	def init_lock(self, proto):
		'''Send data to device via twisted server.'''
		message_type = SERVER_TYPE['lock']
		logger.debug('message_type: {0}'.format(repr(message_type)))
		message_id = get_message_id_for_crc8(proto.message_id)
		controller_id = hex_to_byte(proto.controller_id)
		length = get_length_for_crc8(message_type, message_id, controller_id)
		version = get_version()
		firmware = get_firmware()

		# header
		header = START+length+version+message_type+message_id+firmware+controller_id

		# payload ------------------------------------
		zeros = '\x00' * 15
		signature = 1
		payload = \
			zeros+\
			int_to_byte(signature)

		# -----------------------------------------------

		logger.debug(u'payload length: {0}'.format(len(payload)))

		# aes encryption
		payload = self.aes_encrypt(proto, payload)
		# create crc8
		cmd = header+payload
		crc8_byte = create_crc8_val(cmd)
		lock = cmd+crc8_byte

		logger.debug(u'lock: {0}'.format(repr(lock)))
		# logger.debug(u'lock: {0}'.format(ascii_string(lock)))
		logger.debug(u'Length of lock: {0}'.format(len(lock)))

		crc8_verification(lock)
		proto.token_init_lock = True
		return lock


	''' Receiving section. '''


