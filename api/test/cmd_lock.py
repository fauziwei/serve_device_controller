# coding: utf-8
# @2017
# Fauzi, fauziwei@yahoo.com
import base64
import requests
import requests.exceptions

s = requests.Session()

print(70 * '_') # ------------------------------------------

# GET oauth2 access token.
params = {
	'email': 'fauziwei@yahoo.com',
	'password': '123456'
}

client_id = 'dd8a5f2c-5aac-4ea7-a7a5-db12ebac2a22'
client_secret = 'ba8cfbc9-a75c-404e-9245-80911f3a2a2d'
auth_basic = base64.b64encode('{0}:{1}'.format(client_id, client_secret))
headers = {'Authorization': 'Basic {0}'.format(auth_basic)}

access_token = None
try:
	url = 'http://localhost:7999/oauth2/'
	r = s.get(url, params=params, headers=headers)
	if r.status_code == requests.codes.ok:
		if r.json()['success']:
			access_token = r.json()['access_token']
			expire = r.json()['expire']
			redirect_uri = r.json()['redirect_uri']
			print(u'access_token: {0}'.format(access_token))
			print(u'expire after: {0} seconds'.format(expire))
			print(u'redirect_uri: {0}'.format(redirect_uri))
		else:
			print(r.json()['reason'])

except requests.exceptions.RequestException:
	print(u'Error reach server.')



# POST lock command
print(70 * '_') # ------------------------------------------


if access_token is not None:
	headers = {'Authorization': access_token}

	params = {
		'version': 1,
		'message_id': 10100,
		'firmware': 1,
		'controller_id': 2623632670339818386,
		'signature': 1,
	}

	try:
		url = 'http://localhost:7999/lock/'
		# url = 'http://localhost:7999/api/lock/'
		r = s.post(url, headers=headers, json=params)
		if r.status_code == requests.codes.ok:
			success = r.json()['success']
			print(u'success: {0}'.format(success))
			print(u'reason: {0}'.format(reason))
		else:
			print(u'Unauthorized!')

	except requests.exceptions.RequestException:
		print(u'Error reach server.')

s.close()
