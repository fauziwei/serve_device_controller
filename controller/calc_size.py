import os
import struct
import binascii
from Crypto.Cipher import AES
from utils import *

# float_to_byte = lambda f: struct.pack('f', f)
# byte_to_float = lambda b: struct.unpack('f', b)[0]

# double_to_byte = lambda f: struct.pack('>d', f)
# byte_to_double = lambda b: struct.unpack('>d', byte)[0]

# int_to_byte = lambda i: struct.pack('!H', i)[1:]

def aes_encrypt(self,  data):
	'''data is without crc. Only 16bytes.'''
	IV = os.urandom(16)
	aes = AES.new('02B6111770695324', AES.MODE_ECB, IV=IV)
	ciphertext = aes.encrypt(data)
	return ciphertext


ble_key1 = 'AAAAAAAAAAAAAAAA'
s = hex_to_int(ble_key1)
print s


# zeros = '\x00' * 7
# print repr(zeros)
# print len(zeros)


# ble_key1 = '1234567812345678'
# print repr(hex_to_byte(ble_key1))
# print len(hex_to_byte(ble_key1))


# header = "\xaa\x00\x11\x03Q't\x01$i\x04\x03X\xb6\xe3\x92"
# # payload_before_aes = "\x124Vx\x124Vx\x124Vx\x124Vx\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01"
# # payload_after_aes = ' \x0b;%\xc5\xd9\xe9\xaf\xc3\xd0O\xed\x1c\x05\xe3\x1e\x1a\xc0.\x96\xfd\x04(\xc9!\xda\x98\xfc3\xdf\xf8x'

# payload_before_aes = '\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xbb\xbb\xbb\xbb\xbb\xbb\xbb\xbb\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01'
# payload_after_aes = '\xfdb\xba\xe7%+d\x88\x9e\x82S\xc3\td!\x11\x1a\xc0.\x96\xfd\x04(\xc9!\xda\x98\xfc3\xdf\xf8x'

# cmd = header+payload_before_aes
# # print len(cmd)
# # crc8_0xVal = hex(crc8_func(cmd))
# crc8_0xVal = int_to_hex(crc8_func(cmd))
# print crc8_0xVal
# # crc8_hex = crc8_0xVal.replace('0x', '')
# # print len(crc8_hex)
# # print(crc8_hex)

# cmd = header+payload_after_aes
# # print len(cmd)
# # crc8_0xVal = hex(crc8_func(cmd))
# crc8_0xVal = int_to_hex(crc8_func(cmd))
# print crc8_0xVal
# crc8_hex = crc8_0xVal.replace('0x', '')
# # print len(crc8_hex)
# # print(crc8_hex)

# crc8_byte = binascii.unhexlify(crc8_hex)
# print repr(crc8_byte)