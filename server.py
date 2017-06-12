# coding: utf-8
from twisted.internet import reactor, threads
from twisted.internet.protocol import Factory
from twisted.protocols.basic import LineReceiver
from logic import Logic

# USAGE: ipython server.py

class ServerProtocol(LineReceiver):

	delimiter = '\n'
	peer_ip, peer_port = None, None
	device_id, controller_id = None, None
	unit = None
	belongto_device, belongto_controller = None, None
	token_device, token_controller = False, False

	def __init__(self, factory):
		self.factory = factory

	def connectionMade(self):
		self.peer_ip = self.transport.getPeer().host
		self.peer_port = self.transport.getPeer().port
		# print('Peer: {0}:{1}'.format(self.peer_ip, self.peer_port))

	def connectionLost(self, reason):
		if self.token_controller:
			if self.controller_id in self.factory.controllers.keys():
				del self.factory.controllers[self.controller_id]
				print('Lost connection with controller_id: {0}'.format(self.controller_id))
			self.token_controller = False

		if self.token_device:
			if self.device_id in self.factory.devices.keys():
				del self.factory.devices[self.device_id]
				print('Lost connection with device_id: {0}'.format(self.device_id))
			self.token_device = False

		print('Length of controllers: {0}'.format(len(self.factory.controllers)))
		print('Length of devices: {0}'.format(len(self.factory.devices)))

	def lineReceived(self, data):
		# e.g. data format:
		# the following example only for modifying 1 parameter.
		# device: '666666|30'
		# controller: 'c|device_id|new_unit_setting'
		data = data.split('|')

		if data[0] == 'c': # controller
			# controller: 'c|device_id|new_setting_unit'
			p = threads.deferToThread(self.factory.logic.setting, self, data)
			q = str(reactor.getThreadPool().q.qsize())
			print('Queue after `deferToThread`: {0}\n'.format(q))
			p.addCallback(lambda data: self.send_from_controller(data))
			q = str(reactor.getThreadPool().q.qsize())
			print('Queue after `addCallback`: {0}'.format(q))
		else: # device
			# device: '666666|30'
			p = threads.deferToThread(self.factory.logic.communication, self, data)
			q = str(reactor.getThreadPool().q.qsize())
			print('Queue after `deferToThread`: {0}'.format(q))
			p.addCallback(lambda data: self.send_from_device(data))
			q = str(reactor.getThreadPool().q.qsize())
			print('Queue after `addCallback`: {0}'.format(q))

	def send_from_controller(self, data):
		if self.belongto_device is None:
			# Device not connected to server.
			# Send feedback to controller not success.
			self.sendLine('Device: {0} not connected.'.format(self.controller_id))
		else:
			# Send to device.
			self.belongto_device.sendLine('{0}|{1}'.format(self.controller_id, self.unit))
			# Send to controller.
			self.sendLine('Success.')

	def send_from_device(self, data):
		self.sendLine(data)


class Server(Factory):
	__slots__ = ('logic', 'devices', 'controllers')

	devices, controllers = {}, {}

	def __init__(self):
		self.logic = Logic()

	def buildProtocol(self, addr):
		return ServerProtocol(self)


reactor.listenTCP(8000, Server())
reactor.run()
