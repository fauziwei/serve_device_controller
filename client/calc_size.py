import struct
import binascii
from utils import *

float_to_byte = lambda f: struct.pack('f', f)
byte_to_float = lambda b: struct.unpack('f', b)[0]

double_to_byte = lambda f: struct.pack('>d', f)
byte_to_double = lambda b: struct.unpack('>d', byte)[0]

int_to_byte = lambda i: struct.pack('!H', i)[1:]

print repr(int_to_byte(4))

# latitude = 23.88888888
# lat_byte = double_to_byte(latitude)
# lat_byte_3bytes = lat_byte[0:3]
# lat_byte_5bytes = lat_byte[3:]
# # print len(lat_byte_3bytes)
# # print len(lat_byte_5bytes)

# longitude = 3.66666666
# lon_byte = double_to_byte(longitude)
# lon_byte_3bytes = lon_byte[0:3]
# lon_byte_5bytes = lon_byte[3:]
# # print len(lon_byte_3bytes)
# # print len(lon_byte_5bytes)


# # payload --------------------------------------
# hdware_ver = 1
# upgrade_flag = 1
# lock_status = 1
# csq = 1
# temp = 1
# v_bus = 1
# i_charge = 1
# v_battery = 1
# battery_stat = 1

# # timestamp (4bytes)
# t = get_shanghai_time()
# timestamp = to_timestamp(t)
# timestamp = timestamp_to_byte(timestamp)


# # latitude (split by 2), 3bytes and 5bytes.
# latitude = 23.88888888
# lat_byte = double_to_byte(latitude)
# lat_byte_3bytes = lat_byte[0:3]
# lat_byte_5bytes = lat_byte[3:]

# # longitude (split by 2), 3bytes and 5bytes.
# longitude = 3.66666666
# lon_byte = double_to_byte(longitude)
# lon_byte_3bytes = lon_byte[0:3]
# lon_byte_5bytes = lon_byte[3:]

# fix_flag = 1
# gps_stars = 1
# signature = 1

# payload = \
# 	int_to_byte(hdware_ver)+\
# 	int_to_byte(upgrade_flag)+\
# 	int_to_byte(lock_status)+\
# 	int_to_byte(csq)+\
# 	int_to_byte(temp)+\
# 	int_to_byte(v_bus)+\
# 	int_to_byte(i_charge)+\
# 	int_to_byte(v_battery)+\
# 	int_to_byte(battery_stat)+\
# 	timestamp+\
# 	lat_byte_3bytes+\
# 	lat_byte_5bytes+\
# 	lon_byte_3bytes+\
# 	lon_byte_5bytes+\
# 	int_to_byte(fix_flag)+\
# 	int_to_byte(gps_stars)+\
# 	int_to_byte(signature)

# print len(payload)


# orig
normal_bike_status = 'aa0031034200010124479c0658cd0a18eaf7f5a4b52ac418b43d585d66a09dd5b4a595db644a34ac5518d42893493a0969'
print repr(binascii.unhexlify(normal_bike_status))
print len(binascii.unhexlify(normal_bike_status))

# simu
normal_bike_status = "\xaa\x00\x11\x03B't\x01$i\x04\x03X\xb6\xe3\x92\x9c\xf6\xe5\xb00R\xa3\x83\x80J$\xbe\xe6?\xeb\xddK\xcf\x89c\xb3\x81&jp\xb4\xd2U\xdd\xd7\x85\xfd\x91"
print len(normal_bike_status)


gps_data_report = "aa0031033200030124479c0658cd0a1861c0595ab3891183b7831e87c91b01c3c2a11c628e2a67ec64086d4948546e3cfc"
print repr(binascii.unhexlify(gps_data_report))
print len(binascii.unhexlify(gps_data_report))

# def bin_to_float(b):
# 	""" Convert binary string to a float. """
# 	bf = int_to_bytes(int(b, 2), 8)  # 8 bytes needed for IEEE 754 binary64
# 	return struct.unpack('>d', bf)[0]

# def int_to_bytes(n, minlen=0):  # helper function
# 	""" Int/long to byte string. """
# 	nbits = n.bit_length() + (1 if n < 0 else 0)  # plus one for any sign bit
# 	nbytes = (nbits+7) // 8  # number of whole bytes
# 	b = bytearray()
# 	for _ in range(nbytes):
# 		b.append(n & 0xff)
# 		n >>= 8
# 	if minlen and len(b) < minlen:  # zero pad?
# 		b.extend([0] * (minlen-len(b)))
# 	return bytearray(reversed(b))  # high bytes first

# # tests

# def float_to_bin(f):
# 	""" Convert a float into a binary string. """
# 	ba = struct.pack('>d', f)
# 	ba = bytearray(ba)  # convert string to bytearray - not needed in py3
# 	s = ''.join('{:08b}'.format(b) for b in ba)
# 	return s[:-1].lstrip('0') + s[0] # strip all leading zeros except for last

# # for f in 0.0, 1.0, -14.0, 12.546, 3.141593:
# # 	binary = float_to_bin(f)
# # 	print('float_to_bin(%f): %r' % (f, binary))
# # 	float = bin_to_float(binary)
# # 	print('bin_to_float(%r): %f' % (binary, float))
# # 	print('')



