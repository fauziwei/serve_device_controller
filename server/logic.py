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
from models import Db, Client, User, \
	Status, StatusRecord, InformationRecord, \
	GpsRecord, AbnormalRecord, BleKeyRecord

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
		if proto.device_id not in proto.factory.controllers:
			logger.debug(u'controller_id {0} is not connected.'.format(proto.device_id))
			return

		logger.debug(u'Prepare for relaying data to controller_id: {0}'.format(proto.device_id))
		proto.belongto_controller = proto.factory.controllers[proto.device_id]
		logger.debug(u'Send response success normal_ack: {0}'.format(repr(proto.response_success)))
		proto.belongto_controller.sendLine(proto.response_success)
		# proto.belongto_controller = False
		return

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

		# Cutting received payload 'lock' or 'unlock'
		payload = parsed['payload']

		hdware_ver = payload[0]
		upgrade_flag = payload[1]
		lock_status = payload[2]
		csq = payload[3]
		temp = payload[4]
		vbus = payload[5]
		icharge = payload[6]
		vbattery = payload[7]
		battery_stat = payload[8]
		timestamp = payload[9:13]
		latitude = payload[13:21]
		longitude = payload[21:29]
		fix_flag = payload[29]
		gps_stars = payload[30]
		signature = payload[31]

		# Store to db here...
		session = Db().Session()
		status = session.query(Status).filter_by(device_id=proto.device_id, active=True).first()
		self.commit(session)


		# Send message 'success' to controller.
		if proto.device_id not in proto.factory.controllers:
			logger.debug(u'controller_id {0} is not connected.'.format(proto.device_id))
			return

		logger.debug(u'Prepare for relaying data to controller_id: {0}'.format(proto.device_id))
		proto.belongto_controller = proto.factory.controllers[proto.device_id]
		logger.debug(u'Send response success lock_unlock_response: {0}'.format(repr(proto.response_success)))
		proto.belongto_controller.sendLine(proto.response_success)
		proto.belongto_controller = False
		return

	def gps_data_report_processing(self, proto, parsed):
		'''Preparing relaying gps_data_report from device to controller.'''
		# length = parsed['length']
		# message_type = parsed['message_type']
		# message_id = parsed['message_id']
		# device_id = parsed['device_id']
		# version = parsed['version']
		# firmware = parsed['firmware']

		# Cutting received payload 'gps_data_report'
		payload = parsed['payload']

		latitude = payload[0:8]
		longitude = payload[8:16]
		fig_flag = payload[16]
		# gps_starts_count ???
		gps_stars = payload[17]
		zeros = payload[18:31]
		signature = payload[31]

		# Store to db here...
		session = Db().Session()
		status = session.query(Status).filter_by(device_id=proto.device_id, active=True).first()
		self.commit(session)


		# Send message 'success' to controller.
		if proto.device_id not in proto.factory.controllers:
			logger.debug(u'controller_id {0} is not connected.'.format(proto.device_id))
			return

		logger.debug(u'Prepare for relaying data to controller_id: {0}'.format(proto.device_id))
		proto.belongto_controller = proto.factory.controllers[proto.device_id]
		logger.debug(u'Send response success gps_data_report: {0}'.format(repr(proto.response_success)))
		proto.belongto_controller.sendLine(proto.response_success)
		proto.belongto_controller = False
		return

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

		hdware_ver = payload[0]
		upgrade_flag = payload[1]
		lock_status = payload[2]
		csq = payload[3]
		temp = payload[4]
		vbus = payload[5]
		icharge = payload[6]
		vbattery = payload[7]
		battery_stat = payload[8]
		timestamp = payload[9:13]
		latitude = payload[13:21]
		longitude = payload[21:29]
		fig_flag = payload[29]
		gps_stars = payload[30]
		signature = payload[31]

		# Store to db here...
		session = Db().Session()
		status = session.query(Status).filter_by(device_id=proto.device_id, active=True).first()
		self.commit(session)


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

		hdware_ver = payload[0]
		upgrade_flag = payload[1]
		lock_status = payload[2]
		csq = payload[3]
		temp = payload[4]
		vbus = payload[5]
		icharge = payload[6]
		s_vbattery = payload[7]
		s_battery_stat = payload[8]
		timestamp = payload[9:13]
		latitude = payload[13:21]
		longitude = payload[21:29]
		fig_flag = payload[29]
		# gps_stars_count ???
		gps_stars = payload[30]
		rid_speed = payload[31]
		limit_speed = payload[32]
		gear = payload[33]
		m_vbattery = payload[34:36]
		m_battery_stat = payload[36]
		m_battery_cab = payload[37]
		m_bat_is = payload[38]
		m_bat_cycle_cnt = payload[39]

		# Store to db here...
		session = Db().Session()
		status = session.query(Status).filter_by(device_id=proto.device_id, active=True).first()
		self.commit(session)


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

		hdware_ver = payload[0]
		abnormal = payload[1]
		fault = payload[2]
		zeros = payload[3:15]
		signature = payload[15]

		# Store to db here...
		session = Db.Session()
		status = session.query(Status).filter_by(device_id=proto.device_id, active=True).first()
		self.commit(session)


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
		# length = parsed['length']
		# message_type = parsed['message_type']
		# Server should update device status here, by saving to database.
		# message_id = parsed['message_id'] # Check the status.
		# device_id = parsed['device_id']
		# version = parsed['version']
		# firmware = parsed['firmware']

		# Cutting received payload 'ble_key_response'
		payload = parsed['payload']

		ble_key1 = payload[0:8]
		ble_key2 = payload[8:16]
		zeros = payload[16:31]
		signature = payload[31]

		# Store to db here...
		session = Db.Session()
		status = session.query(Status).filter_by(device_id=proto.device_id, active=True).first()
		self.commit(session)


		# Send message 'success' to controller.
		if proto.device_id not in proto.factory.controllers:
			logger.debug(u'controller_id {0} is not connected.'.format(proto.device_id))
			return

		logger.debug(u'Prepare for relaying data to controller_id: {0}'.format(proto.device_id))
		proto.belongto_controller = proto.factory.controllers[proto.device_id]
		logger.debug(u'Send response success ble_key_response: {0}'.format(repr(proto.response_success)))
		proto.belongto_controller.sendLine(proto.response_success)
		proto.belongto_controller = False
		return

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

		# proto.controller_id = byte_to_hex(parsed['device_id'])
		proto.controller_id = hex_to_int(byte_to_hex(parsed['device_id']))

		if proto.controller_id not in proto.factory.devices:
			logger.debug(u'device_id {0} is not connected.'.format(proto.controller_id))
			return

		logger.debug(u'Prepare for relaying data to device_id: {0}'.format(proto.controller_id))
		proto.belongto_device = proto.factory.devices[proto.controller_id]

		# Store connected controller to self.controllers.
		proto.factory.controllers[proto.controller_id] = proto

		# Store connected controller to redis, It will be accessed by its device when do feedback message.
		# the device will search this 'key': proto.controller_id in redis,
		# to determine socket belong to its controller.
		proto.factory.controllers_cache.set(proto.controller_id, '{0}:{1}'.format(proto.factory.server_ip, proto.factory.server_port))
		proto.token_controller = True

		if parsed['message_type'] == SERVER_TYPE['unlock']:
			logger.debug(u'Detected incoming unlock from controller...')
			return self.unlock_processing(data)

		elif parsed['message_type'] == SERVER_TYPE['lock']:
			logger.debug(u'Detected incoming lock from controller...')
			return self.lock_processing(data)

		elif parsed['message_type'] == SERVER_TYPE['fire_gps_starting_up']:
			logger.debug(u'Detected incoming fire_gps_starting_up from controller...')
			return self.fire_gps_starting_up_processing(data)

		elif parsed['message_type'] == SERVER_TYPE['ble_key_update']:
			logger.debug(u'Detected incoming ble_key_update from controller...')
			return self.ble_key_update_processing(data)

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

		# proto.device_id = byte_to_hex(parsed['device_id'])
		proto.device_id = hex_to_int(byte_to_hex(parsed['device_id']))

		# Store connected device to self.devices
		proto.factory.devices[proto.device_id] = proto

		# Store connected device to redis, later, it will be accessed by its controller.
		# The controler will search this 'key': proto.device_id in redis,
		# and then get value of ipaddr:port to determine, in which twisted server the device is connected.
		# and then controler can login to the certain twisted server.
		proto.factory.devices_cache.set(proto.device_id, '{0}:{1}'.format(proto.factory.server_ip, proto.factory.server_port))
		proto.token_device = True

		if parsed['message_type'] == CLIENT_TYPE['heartbeat']:
			logger.debug(u'Detected incoming heartbeat from device...')
			return self.heartbeat_processing(proto, parsed)

		if parsed['message_type'] == CLIENT_TYPE['normal_ack']:
			# 1st reply fire_gps_starting_up
			logger.debug(u'Detected incoming normal_ack from device...')
			return self.normal_ack_processing(proto, parsed)

		elif parsed['message_type'] == CLIENT_TYPE['lock_unlock_response']:
			logger.debug(u'Detected incoming lock_unlock_response from device...')
			return self.lock_unlock_response_processing(proto, parsed)

		elif parsed['message_type'] ==  CLIENT_TYPE['gps_data_report']:
			logger.debug(u'Detected incoming gps_data_report from device...')
			return self.gps_data_report_processing(proto, parsed)

		elif parsed['message_type'] ==  CLIENT_TYPE['normal_bike_status']:
			logger.debug(u'Detected incoming normal_bike_status from device...')
			return self.normal_bike_status_processing(proto, parsed)

		elif parsed['message_type'] ==  CLIENT_TYPE['pedelec_status_report']:
			logger.debug(u'Detected incoming pedelec_status_report from device...')
			return self.pedelec_status_report_processing(proto, parsed)

		elif parsed['message_type'] ==  CLIENT_TYPE['fault_report']:
			logger.debug(u'Detected incoming fault_report from device...')
			return self.fault_report_processing(proto, parsed)

		elif parsed['message_type'] ==  CLIENT_TYPE['ble_key_response']:
			logger.debug(u'Detected incoming ble_key_response from device...')
			return self.ble_key_response_processing(proto, parsed)

		elif parsed['message_type'] ==  CLIENT_TYPE['command_response']:
			logger.debug(u'Detected incoming command_response from device...')
			return self.command_response_processing(proto, parsed)

		elif parsed['message_type'] ==  CLIENT_TYPE['upgrade_push_response']:
			logger.debug(u'Detected incoming upgrade_push_response from device...')
			return self.upgrade_push_response_processing(proto, parsed)

		elif parsed['message_type'] ==  CLIENT_TYPE['upgrade_data_request']:
			logger.debug(u'Detected incoming upgrade_data_request from device...')
			return self.upgrade_data_request_processing(proto, parsed)

		else:
			logger.debug(u'Client Type from device is not correct. Drop connection.')
			proto.transport.loseConnection()

		return
