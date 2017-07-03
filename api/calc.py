import time
import struct
import pytz
import datetime
import calendar

def get_shanghai_time():
	tz = pytz.timezone('Asia/Shanghai')
	return datetime.datetime.now(tz)

def to_timestamp(t):
	'''
	t = get_shanghai_time()
	ts = to_timestamp(t)
	'''
	# return round( time.mktime(t.timetuple()) )
	return round( calendar.timegm(t.timetuple()) )

def timestamp_to_byte(ts):
	return struct.pack('<I', ts)


t = get_shanghai_time()
print t
ts = to_timestamp(t)
print ts
print repr(timestamp_to_byte(ts))

# print '-------------'

future_t = t + datetime.timedelta(minutes=2)
print future_t
ts = to_timestamp(future_t)
print ts
print repr(timestamp_to_byte(ts))

t = 1499127317.0 - 1499127197.0
print t