# coding: utf-8
# @2017
# Fauzi, fauziwei@yahoo.com

class Logic(object):

	def setting(self, proto, data):
		'''proto is parent's self.'''
		proto.controller_id = data[1]
		proto.unit = data[2]

		if proto.controller_id in proto.factory.devices:

			proto.belongto_device = proto.factory.devices[proto.controller_id]
			print('Relayed to device: {0}'.format(proto.controller_id))

			# Store connected controller into self.controllers.
			proto.factory.controllers[proto.controller_id] = proto

			# Store to cache.
			# proto.controller_id = proto.factory.server_ip
			proto.factory.controllers_cache.set(proto.controller_id, '{0}:{1}'.format(proto.factory.server_ip, proto.factory.server_port))

			proto.token_controller = True
			return 'Connected.'

		return 'Not connected.'

	def communication(self, proto, data):
		'''proto is parent's self.'''
		proto.device_id = data[0]
		proto.unit = data[1]

		# Store connected device into self.devices.
		proto.factory.devices[proto.device_id] = proto

		# Store to cache for controlling purpose.
		proto.factory.devices_cache.set(proto.device_id, '{0}:{1}'.format(proto.factory.server_ip, proto.factory.server_port))

		proto.token_device = True
		return 'Connected.'
