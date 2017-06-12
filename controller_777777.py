# coding: utf-8
from twisted.internet import reactor
from twisted.internet.protocol import ClientFactory
from twisted.protocols.basic import LineReceiver

# USAGE: ipython controller_777777.py

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
reactor.connectTCP('localhost', 8000, Controller(controller_id, unit))
reactor.run()
