# coding: utf-8
# @2017
# Fauzi, fauziwei@yahoo.com
from tornado.web import url
from handlers import UnLock, Lock, FireGpsStartingUp, BleKeyUpdate

url_patterns = [
	url(r'/unlock/', UnLock, name='post unLock.'),
	url(r'/lock/', Lock, name='post lock.'),
	url(r'/fire_gps_starting_up/', FireGpsStartingUp, name='post fire_gps_starting_up.'),
	url(r'/ble_key_update/', BleKeyUpdate, name='post ble_key_update.'),
]
