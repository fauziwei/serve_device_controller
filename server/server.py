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

	def connectionMade(self):
		# Limiting active_connections.
		logger.debug( 30 * u'-' )
		self.active_connection += 1
		if self.active_connection > self.factory.max_connection:
			logger.debug(u'Reaching max connection. Drop connection.')
			self.transport.loseConnection()

	def connectionLost(self, reason):
		self.active_connection -= 1

		if self.token_controller:
			# Remove in controllers.
			if self.controller_id in self.factory.controllers.keys():
				del self.factory.controllers[self.controller_id]
			# Remove in controllers cache.
			if self.factory.controllers_cache.exists(self.controller_id):
				self.factory.controllers_cache.delete(self.controller_id)
			logger.debug(u'Lost connection with controller_id: {0}'.format(self.controller_id))
			self.token_controller = False

		if self.token_device:
			# Remove in devices.
			if self.device_id in self.factory.devices.keys():
				del self.factory.devices[self.device_id]
			# Remove in devices cache.
			if self.factory.devices_cache.exists(self.device_id):
				self.factory.devices_cache.delete(self.device_id)
			logger.debug(u'Lost connection with device_id: {0}'.format(self.device_id))
			self.token_device = False

		logger.debug(u'Size of controllers: {0}'.format(len(self.factory.controllers)))
		logger.debug(u'Size of devices: {0}'.format(len(self.factory.devices)))
		logger.debug(u'Active connections: {0}'.format(self.active_connection))

	def lineReceived(self, data):
		logger.debug(u'Recv: {0}'.format(repr(data)))
		# Assume that the incoming controller message from API
		# is started by 'controller...',
		# e.g: 'controlleraa01...'.
		# Format data after 'controller' is HEX (normal data according to table format)
		if data[0:10] == 'controller':
			# Incoming data from controller.
			p = threads.deferToThread(self.factory.logic.setting, self, data)
			p.addCallback(lambda data: self.sendFromController(data[10:]))
		else:
			# Incoming data from device.
			p = threads.deferToThread(self.factory.logic.communication, self, data)
			p.addCallback(lambda data: self.sendFromDevice(data))

	def sendFromController(self, data):
		if not self.belongto_device:
			# Device not connected to server.
			# Send feedback to controller not success.
			self.sendLine(u'Device: {0} not connected to twisted.'.format(self.controller_id))
		else:
			# Send to device.
			# You need to determine what command want to send to device
			# For lock/Unlock. The command should be invoked by API.
			self.belongto_device.sendLine(u'Some Message Format here...')
			# Send to controller.
			# You may determine other reply command.
			self.sendLine(u'Success.')

	def sendFromDevice(self, data):
		if data:
			logger.debug(u'Send: {0}'.format(repr(data)))
			self.sendLine(data)


# Configuration. --------------------------
server_ip, server_port = '127.0.0.1', 8001
redis_ip, redis_port = '127.0.0.1', 6379
max_connection = 10
# -----------------------------------------

class BFactory(Factory):
	protocol = BProtocol

	max_connection = max_connection
	devices, controllers = {}, {}
	logic = Logic()

	server_ip, server_port = server_ip, server_port
	redis_ip, redis_port = redis_ip, redis_port

	def __init__(self):
		d = {'host': redis_ip, 'port': redis_port, 'db': 0}
		c = {'host': redis_ip, 'port': redis_port, 'db': 1}

		self.devices_cache = Cache(**d)
		self.controllers_cache = Cache(**c)

		self.devices_cache.flushdb()
		self.controllers_cache.flushdb()


def run():
	reactor.listenTCP(server_port, BFactory())
	reactor.run()

if __name__ == '__main__':
	# test = BFactory().buildProtocol(server_ip)
	# test.lineReceived('xxx')
	logger.debug(u'Server started at port: {0}'.format(server_port))
	run()
