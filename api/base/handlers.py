# coding: utf-8
# @2017
# Fauzi, fauziwei@yahoo.com
import logging
import traceback
from tornado import web
from sqlalchemy.exc import IntegrityError

logger = logging.getLogger(__name__)

class BaseHandler(web.RequestHandler):
	def __init__(self, *args, **kwargs):
		super(BaseHandler, self).__init__(*args, **kwargs)

	@property
	def devices_cache(self):
		return self.application.devices_cache

	@property
	def access_token_cache(self):
		return self.application.access_token_cache

	@property
	def models(self):
		return self.application.models

	def commit(self, session):
		try:
			session.flush()
			session.commit()
		except IntegrityError:
			session.rollback()
			logger.debug(u'Exception IntegrityError.')
		except:
			traceback.print_exc()
			session.rollback()
			logger.debug(u'Exception commit.')
		finally:
			session.close()
