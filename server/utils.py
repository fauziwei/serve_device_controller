# coding: utf-8
# @2017
# Fauzi, fauziwei@yahoo.com
import ctypes
import logging
import binascii
import crcmod.predefined

logger = logging.getLogger(__name__)

def uni_to_hex(u):
	return binascii.hexlify(u)

def uni_to_byte(u):
	return binascii.unhexlify(u)

def byte_to_hex(b):
	return binascii.hexlify(b)

def hex_to_byte(h):
	return binascii.unhexlify(h)

def int_to_hex(i):
	# return '0x{0:02x}'.format(i)
	return '{0:02x}'.format(i)

def hex_to_int(h):
	return int(h, 16)

def int32_to_uint32(i):
	return ctypes.c_uint32(i).value

ascii_string = lambda s: ''.join(map(lambda c: "%02X " % ord(c), s))

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
	crc8_func = crcmod.predefined.mkPredefinedCrcFun('crc-8')
	crc8_0xVal = hex(crc8_func(cmd))
	crc8_hex = crc8_0xVal.replace('0x', '')
	crc8_byte = binascii.unhexlify(crc8_hex)
	logger.debug('vrfy_crc: {0} , crc: {1}'.format(repr(crc8_byte), repr(data[-1:])))
	return crc8_byte == data[-1:]

def create_crc8_val(data):
	'''data is full data bytesstream arrive from the network.'''
	crc8_func = crcmod.predefined.mkPredefinedCrcFun('crc-8')
	crc8_0xVal = hex(crc8_func(data))
	crc8_hex = crc8_0xVal.replace('0x', '')
	crc8_byte = binascii.unhexlify(crc8_hex)
	return crc8_byte
