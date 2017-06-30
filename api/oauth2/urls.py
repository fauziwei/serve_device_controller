# coding: utf-8
# @2017
# Fauzi, fauziwei@yahoo.com
from tornado.web import url
from handlers import Oauth2, User

url_patterns = [
	url(r'/oauth2/', Oauth2, name='get oauth2.'),
	url(r'/user/', User, name='get user.'),
]
