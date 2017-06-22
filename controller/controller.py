# coding: utf-8
# @2017
# Fauzi, fauziwei@yahoo.com
import os
import sys
import logging
from twisted.internet import reactor
from twisted.internet.protocol import ClientFactory
from twisted.protocols.basic import LineReceiver
from twisted.internet.error import ReactorNotRunning

# local import
from cache import Cache

reload(sys)
sys.setdefaultencoding('utf-8')

basedir = os.path.abspath(os.path.dirname(__file__))
logging.basicConfig(
	filename = os.path.join(basedir, 'logs', os.path.splitext(os.path.basename(__file__))[0]),
	level = logging.DEBUG, format = '%(asctime)s %(message)s'
)
logger = logging.getLogger(__name__)


class CProtocol(LineReceiver):

	delimiter = '\n'
	# Sample of message_id.
	message_id = 10100

	def connectionMade(self):
		self.peer_ip = self.transport.getPeer().host
		self.peer_port = self.transport.getPeer().port

		logger.debug( 30 * u'-' )
		print(u'Get connection with {0}:{1}'.format(self.peer_ip, self.peer_port))

		# Send message to device via twisted server.
		# The following sample message is 'unlock'
		# msg = 'controlleraa00110301277401ffffffffffffffff60'
		msg = 'controlleraa00110311277401ffffffffffffffffab'
		print(u'Send: {0}'.format(repr(msg)))
		self.sendLine(msg)

	def connectionLost(self, reason):
		print(u'Lost connection with: {0}:{1}'.format(self.peer_ip, self.peer_port))
		if not ReactorNotRunning:
			reactor.stop()

	def lineReceived(self, data):
		print(u'Recv: {0}'.format(repr(data)))


# Configuration -------------------------
# controller_id = 'FFFFFFFFFFFFFFFF'
controller_id = 'ffffffffffffffff'
redis_ip, redis_port = '127.0.0.1', 6379
# ---------------------------------------

class CFactory(ClientFactory):
	protocol = CProtocol

	def __init__(self, controller_id):
		self.controller_id = controller_id


d = {'host': redis_ip, 'port': redis_port, 'db': 0}
devices_cache = Cache(**d)

addr_port = devices_cache.get(controller_id)
if not addr_port:
	print(u'Device: {0} doesnt exist in redis.'.format(controller_id))
	sys.exit(0)

addr, port = addr_port.split(':')
port = int(port)


if __name__ == '__main__':
	# Connected to HA.
	reactor.connectTCP(addr, port, CFactory(controller_id))
	reactor.run()
