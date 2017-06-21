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

from header import *
from utils import *
from logic import Logic

reload(sys)
sys.setdefaultencoding('utf-8')

basedir = os.path.abspath(os.path.dirname(__file__))
logging.basicConfig(
	filename = os.path.join(basedir, 'logs', os.path.splitext(os.path.basename(__file__))[0]),
	level = logging.DEBUG, format = '%(asctime)s %(message)s'
)
logger = logging.getLogger(__name__)

# USAGE: ipython client.py

class CProtocol(LineReceiver):

	delimiter = '\n'
	message_id = 10100 # it suppposed increase by one.
	# device_id = 'ABCDAAAABBBBCCCC'
	device_id = 'FFFFFFFFFFFFFFFF'

	# token for initiator test sending.
	token_init_heartbeat = False

	def connectionMade(self):
		self.peer_ip = self.transport.getPeer().host
		self.peer_port = self.transport.getPeer().port

		logger.debug( 30 * u'-' )
		logger.debug(u'Get connection with {0}:{1}'.format(self.peer_ip, self.peer_port))

		if not self.token_init_heartbeat:
			heartbeat = self.factory.logic.init_heartbeat(self)
			logger.debug(u'Send heartbeat: {0}'.format(repr(heartbeat)))
			self.sendLine(heartbeat)

	def connectionLost(self, reason):
		logger.debug(u'Lost connection with: {0}:{1}'.format(self.peer_ip, self.peer_port))
		if not ReactorNotRunning:
			reactor.stop()

	def lineReceived(self, data):
		logger.debug(u'Recv: {0}'.format(repr(data)))
		# heartbeat = self.factory.logic.init_heartbeat(self)
		# self.sendLine(heartbeat)


class CFactory(ClientFactory):
	protocol = CProtocol
	logic = Logic()

reactor.connectTCP('localhost', 8001, CFactory())
reactor.run()
