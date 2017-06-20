# coding: utf-8
# @2017
# Fauzi, fauziwei@yahoo.com
import sys
import logging
import binascii
from header import *
from utils import *

reload(sys)
sys.setdefaultencoding('utf-8')

logger = logging.getLogger(__name__)

class Logic(object):

	def parsing_crc8(self, data):
		'''Cut recv_data.
		Data is supposed in ByteStream with length 17bytes
		'''
		if len(data) <> 17:
			logger.debug(u'Parsing 17bytes failed.')
			return

		if not crc8_verification(data):
			logger.debug(u'CRC8 verification failed.')
			return

		start = data[0]
		length = data[1:3]
		version = data[3]
		message_type = data[4]
		message_id = data[5:7]
		firmware = data[7]
		device_id = data[8:-1]
		crc = data[-1:]

		logger.debug(u'start: {0}'.format(byte_to_hex(start)))
		logger.debug(u'length: {0} bytes'.format(hex_to_int(byte_to_hex(length))))
		logger.debug(u'version: {0}'.format(byte_to_hex(version)))
		logger.debug(u'message_type: {0}'.format(byte_to_hex(message_type)))
		logger.debug(u'message_id: {0}'.format(byte_to_hex(message_id)))
		logger.debug(u'firmware: {0}'.format(byte_to_hex(firmware)))
		logger.debug(u'device_id: {0}'.format(byte_to_hex(device_id)))
		logger.debug(u'crc: {0}'.format(repr(crc)))

		return {
			'start': start, 'length': length, 'version': version,
			'message_type': message_type, 'message_id': message_id,
			'firmware': firmware, 'device_id': device_id, 'crc': crc
		}

	def heartbeat_processing(self, proto, parsed):
		length = parsed['length']
		message_type = SERVER_TYPE['normal_ack']
		message_id = parsed['message_id']
		proto.device_id = parsed['device_id']
		version = parsed['version']
		firmware = parsed['firmware']
		# has timestamp
		cmd = START+length+version+message_type+message_id+firmware+proto.device_id
		crc8_byte = create_crc8_val(cmd)
		normal_ack = cmd+crc8_byte

		logger.debug(u'normal_ack: {0}'.format(repr(normal_ack)))
		logger.debug(u'normal_ack: {0}'.format(ascii_string(normal_ack)))
		logger.debug(u'Length of normal_ack: {0}'.format(len(normal_ack)))

		crc8_verification(normal_ack)
		return byte_to_hex(normal_ack)

	def communication(self, proto, data):
		
		data = hex_to_byte(data)
		parsed = self.parsing_crc8(data)
		if not parsed:
			return

		if parsed['message_type'] == CLIENT_TYPE['heartbeat']:
			return self.heartbeat_processing(proto, parsed)
