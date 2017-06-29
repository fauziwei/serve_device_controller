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
from header import *
from utils import *
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


class CProtocol(LineReceiver):

	delimiter = '\n'
	# Sample of message_id.
	message_id = 10100

	token_init_unlock = False
	token_init_lock = False
	token_init_fire_gps_starting_up = False
	token_init_ble_key_update = False

	# controller starting message.
	controller_start = '\xff\xff\xff\xff'

	# Response from twisted server for fail or success.
	response_fail = '\xee\xee\xee\xee\xee\xee\xee\xee'
	response_success = '\xbb\xbb\xbb\xbb\xbb\xbb\xbb\xbb'

	def __init__(self, factory):
		self.factory = factory
		self.controller_id = self.factory.controller_id
		self.aes_key = self.factory.aes_key

	def connectionMade(self):
		self.peer_ip = self.transport.getPeer().host
		self.peer_port = self.transport.getPeer().port

		logger.debug( 30 * u'-' )
		logger.debug(u'Get connection with {0}:{1}'.format(self.peer_ip, self.peer_port))

		# Send message to device via twisted server.
		# reactor.callLater(300, self.connectionLost, '')
		reactor.callLater(10, self.connectionLost, '')

		# if not self.token_init_unlock:
		# 	unlock = self.factory.logic.init_unlock(self)
		# 	unlock = self.controller_start+unlock
		# 	logger.debug(u'Send unlock: {0}'.format(repr(unlock)))
		# 	self.sendLine(unlock)

		# if not self.token_init_lock:
		# 	lock = self.factory.logic.init_lock(self)
		# 	lock = self.controller_start+lock
		# 	logger.debug(u'Send lock: {0}'.format(repr(lock)))
		# 	self.sendLine(lock)

		# if not self.token_init_fire_gps_starting_up:
		# 	fire_gps_starting_up = self.factory.logic.init_fire_gps_starting_up(self)
		# 	fire_gps_starting_up = self.controller_start+fire_gps_starting_up
		# 	logger.debug(u'Send fire_gps_starting_up: {0}'.format(repr(fire_gps_starting_up)))
		# 	self.sendLine(fire_gps_starting_up)

		if not self.token_init_ble_key_update:
			ble_key_update = self.factory.logic.init_ble_key_update(self)
			ble_key_update = self.controller_start+ble_key_update
			logger.debug(u'Send ble_key_update: {0}'.format(repr(ble_key_update)))
			self.sendLine(ble_key_update)

	def connectionLost(self, reason):
		logger.debug(u'Lost connection with: {0}:{1}'.format(self.peer_ip, self.peer_port))
		# if not ReactorNotRunning:
		# 	reactor.stop()
		reactor.stop()

	def lineReceived(self, data):
		logger.debug(u'Recv: {0}'.format(repr(data)))
		if data == self.response_success:
			logger.debug(u'SUCCESS get response from device.')
		elif data == self.response_fail:
			logger.debug(u'FAIL get response from device.')
		else:
			logger.debug(u'ERROR response.')

		logger.debug(u'controller initiate to drop connection.')
		# self.transport.loseConnection()


# Configuration -------------------------
# controller_id = 'FFFFFFFFFFFFFFFF'
# controller_id = 'ffffffffffffffff'
controller_id = '2469040358b6e392'
aes_key = '02B6111770695324'
redis_ip, redis_port = '127.0.0.1', 6379
# ---------------------------------------

class CFactory(ClientFactory):
	protocol = CProtocol
	logic = Logic()

	def __init__(self, controller_id, aes_key):
		self.controller_id = controller_id
		self.aes_key = aes_key

	def buildProtocol(self, addr):
		return CProtocol(self)


d = {'host': redis_ip, 'port': redis_port, 'db': 0}
devices_cache = Cache(**d)

addr_port = devices_cache.get(controller_id)
if not addr_port:
	logger.debug(u'Device: {0} doesnt exist in redis.'.format(controller_id))
	sys.exit(0)

addr, port = addr_port.split(':')
port = int(port)


if __name__ == '__main__':
	# Connected to real twisted, not to HA
	reactor.connectTCP(addr, port, CFactory(controller_id, aes_key))
	reactor.run()
