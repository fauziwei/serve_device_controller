from utils import *

latitude = 23.88888888
lat_byte = double_to_byte(latitude)
lat_byte_3bytes = lat_byte[0:3]
lat_byte_5bytes = lat_byte[3:]

# print repr(lat_byte_3bytes)
# print repr(lat_byte_5bytes)
print repr(lat_byte_3bytes+lat_byte_5bytes)


longitude = 3.66666666
lon_byte = double_to_byte(longitude)
lon_byte_3bytes = lon_byte[0:3]
lon_byte_5bytes = lon_byte[3:]

print repr(lon_byte_3bytes+lon_byte_5bytes)


print '-----'
print byte_to_double(lat_byte)
print byte_to_double(lon_byte)
