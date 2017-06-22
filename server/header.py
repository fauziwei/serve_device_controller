# coding: utf-8
# @2017
# Fauzi, fauziwei@yahoo.com
START = '\xAA'

CLIENT_TYPE = {
  'heartbeat'             : '\x01',
  # 'lock_control'          : '\x10',
  'lock_unlock_response'  : '\x13',
  'gps_data_report'       : '\x32',
  'normal_bike_status'    : '\x42',
  'pedelec_status_report' : '\x43',
  'fault_report'          : '\x44',
  'ble_key_response'      : '\x52',
  'command_response'      : '\x62',
  'upgrade_push_response' : '\x72',
  'upgrade_data_request'  : '\x73'
}

SERVER_TYPE = {
  'normal_ack'            : '\x02',
  # 'lock_control'          : '\x10',
  'unlock'                : '\x11',
  'lock'                  : '\x12',
  'configuration_command' : '\x21',
  'fire_gps_starting_up'  : '\x31',
  'get_device_status'     : '\x41',
  'ble_key_update'        : '\x51',
  'control_command_send'  : '\x61',
  'upgrade_command_push'  : '\x71',
  'upgrade_data_send'     : '\x74'
}
