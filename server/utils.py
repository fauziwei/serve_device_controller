# coding: utf-8
# @2017
# Fauzi, fauziwei@yahoo.com
import ctypes
import logging
import binascii
import crcmod.predefined

logger = logging.getLogger(__name__)

uni_to_hex = lambda u: binascii.hexlify(u)
uni_to_byte = lambda u: binascii.unhexlify(u)
byte_to_hex = lambda b: binascii.hexlify(b)
hex_to_byte = lambda h: binascii.unhexlify(h)
# int_to_hex = lambda i: '0x{0:02x}'.format(i)
int_to_hex = lambda i: '{0:02x}'.format(i)
hex_to_int = lambda h: int(h, 16)

int32_to_uint32 = lambda i: ctypes.c_uint32(i).value
ascii_string = lambda s: ''.join(map(lambda c: "%02X " % ord(c), s))

crc8_func = crcmod.predefined.mkPredefinedCrcFun('crc-8')

def convert_length_to_byte(int_len):
	if int_len > 0xFF:
		high = int_len & 0xFF
		low = int_len >> 8
		str_len = chr(low) + chr(high)
	else:
		str_len = '\x00' + chr(int_len)
	return str_len

def crc8_verification(data):
	cmd = data[:-1]
	# crc8_func = crcmod.predefined.mkPredefinedCrcFun('crc-8')
	crc8_0xVal = hex(crc8_func(cmd))
	crc8_hex = crc8_0xVal.replace('0x', '')
	crc8_byte = binascii.unhexlify(crc8_hex)
	logger.debug('vrfy_crc: {0} , crc: {1}'.format(repr(crc8_byte), repr(data[-1:])))
	return crc8_byte == data[-1:]

def create_crc8_val(data):
	'''data is full data bytesstream arrive from the network.'''
	# crc8_func = crcmod.predefined.mkPredefinedCrcFun('crc-8')
	crc8_0xVal = hex(crc8_func(data))
	crc8_hex = crc8_0xVal.replace('0x', '')
	crc8_byte = binascii.unhexlify(crc8_hex)
	return crc8_byte
