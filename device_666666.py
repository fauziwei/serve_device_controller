# coding: utf-8
from twisted.internet import reactor
from twisted.internet.protocol import ClientFactory
from twisted.protocols.basic import LineReceiver
from twisted.internet.error import ReactorNotRunning

# USAGE: ipython device_666666.py

class ClientProtocol(LineReceiver):

	delimiter = '\n'
	peer_ip, peer_port = None, None

	def __init__(self, factory):
		self.factory = factory

	def connectionMade(self):
		self.peer_ip = self.transport.getPeer().host
		self.peer_port = self.transport.getPeer().port
		print('Peer: {0}:{1}'.format(self.peer_ip, self.peer_port))

		self.sendLine('{0}|{1}'.format(self.factory.device_id, self.factory.unit))

	def connectionLost(self, reason):
		print('Lost connection with: {0}'.format(self.peer_ip))
		if not ReactorNotRunning:
			reactor.stop()

	def lineReceived(self, data):
		# self.transport.loseConnection()
		data = data.split('|')
		if len(data) == 2:
			self.factory.unit = data[1]
			print('modify unit to: {0}'.format(self.factory.unit))
		else:
			print('{0}'.format(data))


class Client(ClientFactory):
	__slots__ = ('device_id', 'unit')

	def __init__(self, device_id, unit):
		self.device_id = device_id
		self.unit = unit

	def buildProtocol(self, addr):
		return ClientProtocol(self)

device_id, unit = '666666', '30'
reactor.connectTCP('localhost', 8000, Client(device_id, unit))
reactor.run()
