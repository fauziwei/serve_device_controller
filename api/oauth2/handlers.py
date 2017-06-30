# coding: utf-8
# @2017
# Fauzi, fauziwei@yahoo.com
import sys
import json
import uuid
import base64
import logging
import hashlib
from tornado import gen
# local import
from base.handlers import BaseHandler
from lib.decorator import access_token

reload(sys)
sys.setdefaultencoding('utf-8')

logger = logging.getLogger(__name__)


class Oauth2(BaseHandler):

	@gen.coroutine
	def get(self, *args, **kwargs):

		# check headers.
		headers = self.request.headers.get('Authorization', None)
		if headers is None or not headers.startswith('Basic '):
			reason = u'Incorrect base64.'
			logger.debug(reason)
			self.finish( json.dumps({'success': False, 'reason': reason}) )
			return

		logger.debug(u'headers: {0}'.format(headers))

		try:
			decoded = base64.decodestring(headers[6:])
			logger.debug(u'decoded: {0}'.format(decoded))
			client_id, client_secret = decoded.split(':', 2)
		except:
			reason = u'Exception headers decoding.'
			logger.debug(reason)
			self.finish( json.dumps({'success': False, 'reason': reason}) )
			return

		session = self.models.Db().Session()
		client = session.query(self.models.Client).filter_by(id=client_id, secret=client_secret).first()
		if not client:
			self.commit(session)
			reason = u'Incorrect client_id/ client_secret.'
			logger.debug(reason)
			self.finish( json.dumps({'success': False, 'reason': reason}) )
			return

		self.commit(session)

		# check body
		email = self.get_argument('email', None)
		password = self.get_argument('password', None)

		if email is None or password is None:
			reason = u'Required email and password.'
			logger.debug(reason)
			self.finish( json.dumps({'success': False, 'reason': reason}) )
			return

		session = self.models.Db().Session()
		user = session.query(self.models.User).filter_by(email=email).first()
		if not user:
			self.commit(session)
			reason = u'User doesnt exist.'
			logger.debug(reason)
			self.finish( json.dumps({'success': False, 'reason': reason}) )
			return

		user_id = user.id
		salt = user.salt
		prepare_password = hashlib.md5(password).hexdigest()
		secure_password = u'{0}{1}'.format(prepare_password, salt)
		hashed_password = hashlib.md5(secure_password).hexdigest()

		if user.password <> hashed_password:
			self.commit(session)
			reason = u'Incorrect password.'
			logger.debug(reason)
			self.finish( json.dumps({'success': False, 'reason': reason}) )
			return

		self.commit(session)

		_ = True
		while _:
			acc_token = str(uuid.uuid4())
			grant = self.access_token_cache.exists(acc_token)
			if not grant:
				_ = False

		grant = {'user_id': user_id, 'client_id': client_id, 'email': email}
		self.access_token_cache.save_dict(acc_token, grant)
		expire = 86400
		self.access_token_cache.expire(acc_token, expire)

		# send acc_token to user for next headers login.
		self.finish( json.dumps({
			'success': True,
			'access_token': acc_token,
			'expire': expire,
			'redirect_uri': 'Please read the docs.'
		}) )


class User(BaseHandler):
	
	@gen.coroutine
	@access_token
	def get(self, *args, **kwargs):

		email = self.get_argument('email', None)

		session = self.models.Db().Session()

		if email is None:
			users = session.query(self.models.User).order_by(self.models.User.email).all()
		else:
			users = session.query(self.models.User).filter(self.models.User.email.like('%{}%'.format(email))).all()

		_users = []

		iterator = iter(users)
		while True:
			try:
				user = next(iterator)
				d = {
					'id': user.id,
					'email': user.email
				}
				_users.append(d)
			except StopIteration:
				break
	
		self.commit(session)
		self.finish( json.dumps({'success': True, 'users': _users}) )
