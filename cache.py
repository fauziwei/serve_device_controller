# coding: utf-8
# @2017
# Fauzi, fauziwei@yahoo.com
try:
	import dill
	import pickle
except ImportError:
	import dill as pickle
import redis
import redis.exceptions

class Cache(object):
	'''Redis, Pickle.'''

	def __init__(self, *args, **kwargs):
		self.rds = redis.StrictRedis(
			host=kwargs['host'], port=kwargs['port'], db=kwargs['db']
		)

	def set(self, key, value):
		self.rds.set(key, value)

	def get(self, key):
		return self.rds.get(key)

	def set_dumps(self, key, value):
		'''value is self.'''
		self.rds.set(key, pickle.dumps(value))

	def get_dumps(self, key):
		return pickle.loads(self.rds.get(key))

	def exists(self, key):
		return self.rds.exists(key)

	def delete(self, key):
		'''Delete key/value from redis.'''
		try:
			self.rds.delete(key)
		except redis.exceptions.ResponseError:
			raise

	def flushdb(self):
		'''Flush current connection redis database.'''
		self.rds.flushdb()

	def size(self):
		'''Get the size of current redis database.'''
		return self.rds.dbsize()
