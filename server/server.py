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
from twisted.internet.defer import DeferredLock
from logic import Logic

reload(sys)
sys.setdefaultencoding('utf-8')

basedir = os.path.abspath(os.path.dirname(__file__))
logging.basicConfig(
	filename = os.path.join(basedir, 'logs', os.path.splitext(os.path.basename(__file__))[0]),
	level = logging.DEBUG, format = '%(asctime)s %(message)s'
)
logger = logging.getLogger(__name__)

# USAGE: ipython server.py

class BProtocol(LineReceiver):

	delimiter = '\n'
	active_connection = 0

	device_id = None

	def __init__(self):
		self.locker = DeferredLock()

	def connectionMade(self):
		# Limiting the active_connections.
		self.active_connection += 1
		if self.active_connection > self.factory.max_connection:
			logger.debug(u'Reaching max connection.')
			self.transport.loseConnection()

	def connectionLost(self, reason):
		self.active_connection -= 1

	def lineReceived(self, data):
		logger.debug(u'Recv: {0}'.format(repr(data)))
		# Assume the data from device only,
		# controller still not implemented.
		self.locker.acquire().addCallback(self.blockingDevice, data)

	def blockingDevice(self, lock, data):
		p = threads.deferToThread(self.factory.logic.communication, self, data)
		p.addCallback(lambda data: self.sendFromDevice(data))
		lock.release()

	def sendFromDevice(self, data):
		if data:
			logger.debug(u'Send: {0}'.format(repr(data)))
			self.sendLine(data)


class BFactory(Factory):
	protocol = BProtocol

	max_connection = 10
	devices = {}
	logic = Logic()


def run():
	reactor.listenTCP(8001, BFactory())
	reactor.run()

if __name__ == '__main__':
	# test = BFactory().buildProtocol('127.0.0.1')
	# test.lineReceived('xxx')
	logger.debug(u'Server started at port: {0}'.format(8001))
	run()
