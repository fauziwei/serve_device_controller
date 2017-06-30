# coding: utf-8
# @2017
# Fauzi, fauziwei@yahoo.com
import os
import logging
from tornado import web, ioloop, httpserver
from urls import url_patterns
# local import
import lib.cache as cache
import lib.models as models

basedir = os.path.abspath(os.path.dirname(__file__))
logging.basicConfig(
	filename = os.path.join(basedir, 'logs', os.path.splitext(os.path.basename(__file__))[0]),
	level = logging.DEBUG, format = '%(asctime)s %(message)s'
)
logger = logging.getLogger(__name__)


class Application(web.Application):
	settings = {'debug': False}
	d = {'host': '127.0.0.1', 'port': 6379, 'db': 0}
	devices_cache = cache.Cache(**d)

	d = {'host': '127.0.0.1', 'port': 6379, 'db': 2}
	access_token_cache = cache.Cache(**d)

	models = models

	def __init__(self):
		super(Application, self).__init__(url_patterns, **settings)

def run():
	port, address = 7999, '127.0.0.1'
	app = Application()
	server = httpserver.HTTPServer(app)
	server.listen(port, address=address)
	logger.debug(u'Server running on port: {0}'.format(port))
	ioloop.IOLoop.instance().start()

if __name__ == '__main__':
	run()
