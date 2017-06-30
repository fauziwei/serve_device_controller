# coding: utf-8
# @2017
# Fauzi, fauziwei@yahoo.com
import sys
import json
import logging
from tornado import gen
# local import
from base.handlers import BaseHandler
from lib.decorator import access_token

reload(sys)
sys.setdefaultencoding('utf-8')

logger = logging.getLogger(__name__)


class Test(BaseHandler):

	@gen.coroutine
	def get(self, *args, **kwargs):
		self.finish()
