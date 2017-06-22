# coding: utf-8
# @2017
# Fauzi, fauziwei@yahoo.com
import sys
import logging
import binascii

# local import
from header import *
from utils import *
from models import *

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


	''' Sending section. '''

	def unlock_processing(self, proto, parsed):
		'''Relaying data from controller to device.'''
		return 'Unlock message goes here...'

	def lock_processing(self, proto, parsed):
		'''Relaying data from controller to device.'''
		return 'Lock message goes here...'


	''' Receiving section. '''

	def heartbeat_processing(self, proto, parsed):
		length = parsed['length']
		message_type = SERVER_TYPE['normal_ack']
		message_id = parsed['message_id']
		device_id = parsed['device_id']
		version = parsed['version']
		firmware = parsed['firmware']
		# has timestamp
		cmd = START+length+version+message_type+message_id+firmware+device_id
		crc8_byte = create_crc8_val(cmd)
		normal_ack = cmd+crc8_byte

		# logger.debug(u'normal_ack: {0}'.format(repr(normal_ack)))
		logger.debug(u'normal_ack: {0}'.format(ascii_string(normal_ack)))
		logger.debug(u'Length of normal_ack: {0}'.format(len(normal_ack)))

		crc8_verification(normal_ack)
		return byte_to_hex(normal_ack)

	def lock_unlock_response_processing(self, proto, parsed):
		pass

	def gps_data_report_processing(self, proto, parsed):
		pass

	def normal_bike_status_processing(self, proto, parsed):
		pass

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
		data = hex_to_byte(data)
		parsed = self.parsing_crc8(data)
		if not parsed:
			return

		proto.controller_id = byte_to_hex(parsed['device_id'])

		if proto.controller_id not in proto.factory.devices:
			logger.debug(u'Device {0} is not connected.'.format(proto.controller_id))
			return

		logger.debug(u'Prepare for relaying data to device: {0}'.format(proto.controller_id))
		proto.belongto_device = proto.factory.devices[proto.controller_id]

		# Store connected controller to self.controllers.
		proto.factory.controllers[proto.controller_id] = proto

		# Store to connected controller to redis.
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
		data = hex_to_byte(data)
		parsed = self.parsing_crc8(data)
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
			return self.heartbeat_processing(proto, parsed)

		elif parsed['message_type'] == CLIENT_TYPE['lock_unlock_response']:
			return self.lock_unlock_response_processing(proto, parsed)

		elif parsed['message_type'] ==  CLIENT_TYPE['gps_data_report']:
			return self.gps_data_report_processing(proto, parsed)

		elif parsed['message_type'] ==  CLIENT_TYPE['normal_bike_status']:
			return self.normal_bike_status_processing(proto, parsed)

		elif parsed['message_type'] ==  CLIENT_TYPE['pedelec_status_report']:
			return self.pedelec_status_report_processing(proto, parsed)

		elif parsed['message_type'] ==  CLIENT_TYPE['fault_report']:
			return self.fault_report_processing(proto, parsed)

		elif parsed['message_type'] ==  CLIENT_TYPE['ble_key_response']:
			return self.ble_key_response_processing(proto, parsed)

		elif parsed['message_type'] ==  CLIENT_TYPE['command_response']:
			return self.command_response_processing(proto, parsed)

		elif parsed['message_type'] ==  CLIENT_TYPE['upgrade_push_response']:
			return self.upgrade_push_response_processing(proto, parsed)

		elif parsed['message_type'] ==  CLIENT_TYPE['upgrade_data_request']:
			return self.upgrade_data_request_processing(proto, parsed)

		else:
			logger.debug(u'Client Type is not correct. Drop connection.')
			proto.transport.loseConnection()

		return
