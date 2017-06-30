# coding: utf-8
# @2017
# Fauzi, fauziwei@yahoo.com
from tornado.web import url
from handlers import Test

url_patterns = [
	url(r'/test/', Test, name='get test.'),
]
