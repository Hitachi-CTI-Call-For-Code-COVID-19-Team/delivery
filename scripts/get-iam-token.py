#!/usr/bin/env python3

# a script to get a IAM token to the IBM Cloud
# This requires an environment variable ${APIKEY} as your IAM API key.

import os
import json
from urllib import request

# get IAM token
print('Starting to get an token')
data = 'grant_type=urn:ibm:params:oauth:grant-type:apikey&apikey={}'.format(os.environ.get('APIKEY')).encode()
headers = {'Content-Type': 'application/x-www-form-urlencoded'}
req = request.Request('https://iam.cloud.ibm.com/oidc/token', data = data, headers = headers)
r = request.urlopen(req)
token = 'Bearer ' + json.loads(r.read())['access_token']
print('done\n')
print(token)