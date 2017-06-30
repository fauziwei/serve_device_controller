# coding: utf-8
# @2017
# Fauzi, fauziwei@yahoo.com
import redis
import redis.exceptions

class Cache(object):

	def __init__(self, *args, **kwargs):
		self.rds = redis.StrictRedis(
			host=kwargs['host'], port=kwargs['port'], db=kwargs['db']
		)

	def expire(self, key, ttl):
		'''set the expire key.

		ttl in second.
		1 day = 86400
		1 week = 604800

		'''
		self.rds.expire(key, ttl)

	def set(self, key, value):
		'''Store to redis.'''
		self.rds.set(key, value)

	def get(self, key):
		'''Get value based on key.'''
		return self.rds.get(key)

	def exists(self, key):
		'''Check existing key.
		return True/False
		'''
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

	def save_dict(self, key, value):
		'''key is a string and value is a dict.'''
		self.rds.hmset(key, value)

	def get_dict(self, key):
		'''Get value dictionary.'''
		return self.rds.hgetall(key)
