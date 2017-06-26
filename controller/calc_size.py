import struct
import binascii
from utils import *

float_to_byte = lambda f: struct.pack('f', f)
byte_to_float = lambda b: struct.unpack('f', b)[0]

double_to_byte = lambda f: struct.pack('>d', f)
byte_to_double = lambda b: struct.unpack('>d', byte)[0]

int_to_byte = lambda i: struct.pack('!H', i)[1:]


zeros = '\x00' * 7
print repr(zeros)
print len(zeros)
