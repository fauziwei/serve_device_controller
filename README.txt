
NOTE:
- REDIS SETTING WITHOUT AUTH, otherwise is required to edit cache.py
- MySQL requred user and password, is required to edit models.py
- device_id is lower case, otherwise change function 'int_to_hex' in utils.py


For testing purpose, is required to open 5 consoles:

1. 1st console (to run server-app)
   $ server.py
2. 2nd console (to see running server-log)
   $ tail -f logs/server

3. 3rd console (to run client-app), for testing purpose
   $ client.py
4. 4th console (to see running client-log)
   $ tail -f logs/client

5. 5th console (to run controller-app), for testing purpose
   $ controller.py



IN SERVER:
- redis will utilized db=0 for devices_cache db=1 for controllers_cache


First:
1. Client initiate by sending 'normal_bike_status' without aes.
2. Server Reply with normal_ack
3. Maintain...


Second:
1. Controller initiate send 'unlock'
2. Server will auto reply to Client:
3. Controller will receive 2 kind of response:
   Success: '\xbb\xbb\xbb\xbb\xbb\xbb\xbb\xbb'
   Fail: '\xee\xee\xee\xee\xee\xee\xee\xee'
