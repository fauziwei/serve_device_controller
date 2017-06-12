# coding: utf-8

class Logic(object):

	def setting(self, proto, data):
		'''proto is parent's self.'''
		proto.controller_id = data[1]
		proto.unit = data[2]

		if proto.controller_id in proto.factory.devices:
			proto.belongto_device = proto.factory.devices[proto.controller_id]
			print('Relayed to device: {0}'.format(proto.controller_id))

			# Store connected controller into self.controllers 
			proto.factory.controllers[proto.controller_id] = proto
			proto.token_controller = True
			return 'Connected.'

		return 'Not connected.'

	def communication(self, proto, data):
		'''proto is parent's self.'''
		proto.device_id = data[0]
		proto.unit = data[1]

		# Store connected device into self.devices
		proto.factory.devices[proto.device_id] = proto
		proto.token_device = True
		return 'Connected.'
