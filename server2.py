# coding: utf-8
# @2017
# Fauzi, fauziwei@yahoo.com
from platform import system
if system().lower() == 'windows':
	from twisted.internet import iocpreactor
	iocpreactor.install()
else:
	from twisted.internet import epollreactor
	epollreactor.install()
from twisted.internet import reactor, threads
from twisted.internet.protocol import Factory
from twisted.protocols.basic import LineReceiver
from cache import Cache
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
			# remove in controllers.
			if self.controller_id in self.factory.controllers.keys():
				del self.factory.controllers[self.controller_id]
			# remove in controllers cache.
			if self.factory.controllers_cache.exists(self.controller_id):
				self.factory.controllers_cache.delete(self.controller_id)
			print('Lost connection with controller_id: {0}'.format(self.controller_id))
			self.token_controller = False

		if self.token_device:
			# remove in devices.
			if self.device_id in self.factory.devices.keys():
				del self.factory.devices[self.device_id]
			# remove in devices cache.
			if self.factory.devices_cache.exists(self.device_id):
				self.factory.devices_cache.delete(self.device_id)
			print('Lost connection with device_id: {0}'.format(self.device_id))
			self.token_device = False

		print('Size of controllers: {0}'.format(len(self.factory.controllers)))
		print('Size of devices: {0}'.format(len(self.factory.devices)))

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

	devices, controllers = {}, {}

	def __init__(self, *args, **kwargs):

		self.server_ip = kwargs['server_ip']
		self.server_port = kwargs['server_port']
		self.redis_ip = kwargs['redis_ip']
		self.redis_port = kwargs['redis_port']

		d = {'host': self.redis_ip, 'port': self.redis_port, 'db': 0}
		c = {'host': self.redis_ip, 'port': self.redis_port, 'db': 1}

		self.devices_cache = Cache(**d)
		self.controllers_cache = Cache(**c)

		self.devices_cache.flushdb()
		self.controllers_cache.flushdb()

		self.logic = Logic()

	def buildProtocol(self, addr):
		return ServerProtocol(self)


kwargs = {
	'server_ip': '127.0.0.1',
	'server_port': 8002,
	'redis_ip': '127.0.0.1',
	'redis_port': 6379
}
reactor.listenTCP(kwargs['server_port'], Server(**kwargs))
reactor.run()
