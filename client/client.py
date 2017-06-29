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
	# Sample of device_id (sample in HEX)
	# device_id = 'FFFFFFFFFFFFFFFF'
	device_id = '2469040358b6e392'
	# device_id = '2614229659785431576'

	aes_key = '02B6111770695324'

	# token for initiator test sending.
	token_init_heartbeat = False
	token_init_normal_bike_status = False
	token_init_pedelec_status_report = False
	token_init_fault_report = False

	def connectionMade(self):
		self.peer_ip = self.transport.getPeer().host
		self.peer_port = self.transport.getPeer().port

		logger.debug( 30 * u'-' )
		logger.debug(u'Get connection with {0}:{1}'.format(self.peer_ip, self.peer_port))

		# if not self.token_init_heartbeat:
		# 	heartbeat = self.factory.logic.init_heartbeat(self)
		# 	logger.debug(u'Send heartbeat: {0}'.format(repr(heartbeat)))
		# 	self.sendLine(heartbeat)

		# if not self.token_init_normal_bike_status:
		# 	normal_bike_status = self.factory.logic.init_normal_bike_status(self)
		# 	logger.debug(u'Send normal_bike_status: {0}'.format(repr(normal_bike_status)))
		# 	self.sendLine(normal_bike_status)

		# if not self.token_init_pedelec_status_report:
		# 	pedelec_status_report = self.factory.logic.init_pedelec_status_report(self)
		# 	logger.debug(u'Send pedelec_status_report: {0}'.format(repr(pedelec_status_report)))
		# 	self.sendLine(pedelec_status_report)

		if not self.token_init_fault_report:
			fault_report = self.factory.logic.init_fault_report(self)
			logger.debug(u'Send fault_report: {0}'.format(repr(fault_report)))
			self.sendLine(fault_report)

	def connectionLost(self, reason):
		logger.debug(u'Lost connection with: {0}:{1}'.format(self.peer_ip, self.peer_port))
		if not ReactorNotRunning:
			reactor.stop()

	def lineReceived(self, data):
		logger.debug(u'Recv: {0}'.format(repr(data)))
		data = self.factory.logic.communication(self, data)
		if data:
			logger.debug(u'Send: {0}'.format(repr(data)))
			self.sendLine(data)
		else:
			logger.debug(u'Maintain connection...')


class CFactory(ClientFactory):
	protocol = CProtocol
	logic = Logic()

# Connected to HA.
reactor.connectTCP('localhost', 8001, CFactory())
reactor.run()
