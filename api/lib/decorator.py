# coding: utf-8
# @2017
# Fauzi, fauziwei@yahoo.com
import sys
import json
import logging
from functools import wraps

reload(sys)
sys.setdefaultencoding('utf-8')

logger = logging.getLogger(__name__)

def access_token(f):
	'''Decorator for authentication method.'''

	@wraps(f)
	def wrapper(self, *args, **kwargs):

		# Check headers authorization.
		acc_token = self.request.headers.get('Authorization', None)
		if acc_token is None:
			reason = u'access_token doesnt exist in header Authorization.'
			logger.debug(reason)
			self.finish( json.dumps({'success': False, 'reason': reason}) )
			return

		# Check access_token in redis.
		if not self.access_token_cache.exists(acc_token):
			reason = u'access_token doesnt exist in cache.'
			logger.debug(reason)
			self.finish( json.dumps({'success': False, 'reason': reason}) )
			return

		# Get value of access_token in redis.
		grant = self.access_token_cache.get_dict(acc_token)
		logger.debug(u'Login: {0}'.format(grant))

		self.user_id = grant['user_id']
		self.client_id = grant['client_id']
		self.email = grant['email']

		return f(self, *args, **kwargs)

	return wrapper
