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

import os
import sys
import logging
from twisted.internet import reactor, threads
from twisted.internet.protocol import Factory
from twisted.protocols.basic import LineReceiver

# local import
from cache import Cache
from logic import Logic

reload(sys)
sys.setdefaultencoding('utf-8')

basedir = os.path.abspath(os.path.dirname(__file__))
logging.basicConfig(
	filename = os.path.join(basedir, 'logs', os.path.splitext(os.path.basename(__file__))[0]),
	level = logging.DEBUG, format = '%(asctime)s %(message)s'
)
logger = logging.getLogger(__name__)


class BProtocol(LineReceiver):

	delimiter = '\n'
	active_connection = 0

	device_id, controller_id = False, False
	belongto_device, belongto_controller = False, False
	token_device, token_controller = False, False

	# Response to controller for fail or success.
	response_fail = '\xee\xee\xee\xee\xee\xee\xee\xee'
	response_success = '\xbb\xbb\xbb\xbb\xbb\xbb\xbb\xbb'

	def connectionMade(self):
		# Limiting active_connections.
		logger.debug( 30 * u'-' )
		self.active_connection += 1
				
		if self.factory.haproxy_ip == self.transport.getPeer().host:
			if self.active_connection > self.factory.max_connection:
				logger.debug(u'Reaching max connection. Drop connection.')
				self.transport.loseConnection()

	def connectionLost(self, reason):
		self.active_connection -= 1

		if self.token_controller:
			# Remove in controllers.
	
		if self.token_device:
			# Remove in devices.

		logger.debug(u'Total of controllers: {0}'.format(len(self.factory.controllers)))
		logger.debug(u'Total of devices: {0}'.format(len(self.factory.devices)))
		

	def lineReceived(self, data):
		logger.debug(u'Recv: {0}'.format(repr(data)))
		# Assume that the incoming controller message from API
	
	def sendFromController(self, data):
		logger.debug(u'Recv: {0}'.format(repr(data)))

	def sendFromDevice(self, data):
		logger.debug(u'Recv: {0}'.format(repr(data)))


# Configuration. --------------------------
server_ip, server_port = '127.0.0.1', 8001
redis_ip, redis_port = '127.0.0.1', 6379
max_connection = 1000
aes_key = '02B6111770695324'
haproxy_ip = '192.168.8.10' # sample
# -----------------------------------------

class BFactory(Factory):
	protocol = BProtocol

	max_connection = max_connection
	aes_key = aes_key
	devices, controllers = {}, {}
	logic = Logic()

	server_ip, server_port = server_ip, server_port
	redis_ip, redis_port = redis_ip, redis_port


def run():
	reactor.listenTCP(server_port, BFactory())
	reactor.run()

if __name__ == '__main__':
	# test = BFactory().buildProtocol(server_ip)
	# test.lineReceived('xxx')
	logger.debug(u'Server started at port: {0}'.format(server_port))
	run()
