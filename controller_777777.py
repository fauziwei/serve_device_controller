# coding: utf-8
# Fauzi, fauziwei@yahoo.com
import sys
from twisted.internet import reactor
from twisted.internet.protocol import ClientFactory
from twisted.protocols.basic import LineReceiver
from cache import Cache

# USAGE: ipython controller_666666.py

class ControllerProtocol(LineReceiver):

	delimiter = '\n'
	peer_ip, peer_port = None, None

	def __init__(self, factory):
		self.factory = factory

	def connectionMade(self):
		self.peer_ip = self.transport.getPeer().host
		self.peer_port = self.transport.getPeer().port
		print('Peer: {0}:{1}'.format(self.peer_ip, self.peer_port))

		self.sendLine('c|{0}|{1}'.format(self.factory.controller_id, self.factory.unit))

	def connectionLost(self, reason):
		print('Lost connection with: {0}'.format(self.peer_ip))
		reactor.stop()

	def lineReceived(self, data):
		print('recv msg: {0}'.format(data))
		self.transport.loseConnection()


class Controller(ClientFactory):
	__slots__ = ('controller_id', 'unit')

	def __init__(self, controller_id, unit):
		self.controller_id = controller_id
		self.unit = unit

	def buildProtocol(self, addr):
		return ControllerProtocol(self)


controller_id, unit = '777777', '700'

kwargs = {
	'redis_ip': '127.0.0.1',
	'redis_port': 6379
}
d = {'host': kwargs['redis_ip'], 'port': kwargs['redis_port'], 'db': 0}
devices_cache = Cache(**d)

addr_port = devices_cache.get(controller_id)
if not addr_port:
	print('Device: {0} doesnt exist in cache.'.format(controller_id))
	sys.exit(0)

addr, port = addr_port.split(':')
port = int(port)

reactor.connectTCP(addr, port, Controller(controller_id, unit))
reactor.run()
