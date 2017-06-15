try:
	import dill
	import pickle
except ImportError:
	import dill as pickle

import redis

# pickle dump redis
# https://stackoverflow.com/questions/12870772/get-object-from-redis-without-eval

class Test(object):

	def __init__(self):
		# self.d = Dict()
		self.rds = redis.StrictRedis(host='127.0.0.1', port=6379, db=0)

		self.test = 'just test'

	def print_self(self):
		print self

	def set_value(self, key):
		self.rds.set(key, pickle.dumps(self))

	def get_value(self, key):
		return pickle.loads(self.rds.get(key))




t = Test()
# t.print_self()
t.set_value('name')
test =  t.get_value('name')
print test.test