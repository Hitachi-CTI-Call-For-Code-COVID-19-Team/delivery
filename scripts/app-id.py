#!/usr/bin/env python3

# Reference:
# [IBM Cloud App ID API list](https://us-south.appid.cloud.ibm.com/swagger-ui/#/)

import argparse
import subprocess
import os
import json
from urllib import request

class bcolors:
  HEADER = '\033[95m'
  OKBLUE = '\033[94m'
  OKGREEN = '\033[92m'
  WARNING = '\033[93m'
  FAIL = '\033[91m'
  ENDC = '\033[0m'
  BOLD = '\033[1m'
  UNDERLINE = '\033[4m'

# get arguments
parser = argparse.ArgumentParser(description="""
create IBM Cloud App ID instance.
This requires an environment variable ${APIKEY} as your IAM API key.
""")
parser.add_argument(
  '-r', '--region', default='jp-tok', help='Region Name'
)
parser.add_argument(
  '-g', '--resource-group', default='c4c-covid-19', help='Resource Group Name'
)
parser.add_argument(
  '-p', '--service-plan', default='lite', help='Service Plan Name'
)
parser.add_argument(
  '-n', '--instance-name', default='app-id', help='App ID Instance Name'
)
parser.add_argument(
  '-l', '--logo-path', default='hitachi-logo.jpg',
  help='Path to Logo File Used in Login Page. Relative path is Acceptable'
)
parser.add_argument(
  '-e', '--email-confirmation', default='FULL',
  help='''
  FULL|OFF.
  FULL means to verify email address given by signing up.
  OFF doesn't require email verification.
  '''
)
parser.add_argument(
  '-u', '--redirect-urls', default='http://localhost:8080/callback,http://localhost:8081/callback',
  help='''
  Comma-Separated Redirect URL List.
  These should be URLs called back from App ID as well as it should not be '/' which causes ERR_TOO_MANY_REDIRECTS.
  '''
)
parser.add_argument(
  '-a', '--application-names', default='manager-console,signage-view',
  help='''
  Comma-Separaqted Application Names Registered to App ID.
  Note that redirect URLs in the redirect-urls should be the URLs of this app, which are in the same order.
  '''
)
parser.add_argument(
  '-s', '--application-users',
  default='hiroshi.nakagoe.yc@hitachi.com:HiroshiNakagoe:12345678,hiroshi.nakagoe@gmail.com:HiroshiGmail:12345678',
  help='Comma-Separated Application User List. Each User Should Be Comma-Separated Attribute List With EMAIL:USERNAME:PASSWORD'
)

args = parser.parse_args()

# create IBM Cloud App ID instance
print(bcolors.OKGREEN + 'Starting to create an App ID instance' + bcolors.ENDC)
# login
subprocess.check_call(['ibmcloud', 'login', '--apikey', os.environ.get('APIKEY')])
# set target region and resource group
subprocess.check_call(['ibmcloud', 'target', '-r', args.region, '-g', args.resource_group])
# check if an instacne is
p1 = subprocess.Popen(['ibmcloud', 'resource', 'service-instances'], stdout=subprocess.PIPE)
p2 = subprocess.Popen(['grep', args.instance_name], stdin=p1.stdout, stdout=subprocess.PIPE)
p3 = subprocess.Popen(['wc', '-l'], stdin=p2.stdout, stdout=subprocess.PIPE)
res = p3.communicate()[0]

if int(res.decode('utf-8')) == 0:
  # create an instance
  subprocess.check_call(
    ['ibmcloud', 'resource', 'service-instance-create',
     args.instance_name, 'appid', args.service_plan, args.region]
  )

# get tenant ID of App ID
p1 = subprocess.Popen(['ibmcloud', 'resource', 'service-instance', args.instance_name], stdout=subprocess.PIPE)
p2 = subprocess.Popen(['awk', '-F\:', '/^ID/ {print $9}'], stdin=p1.stdout, stdout=subprocess.PIPE)
tenant_id = p2.communicate()[0].decode('utf-8').strip()

# get IAM token
print(bcolors.OKGREEN + 'Starting to get an token for API requests to App ID' + bcolors.ENDC)
data = 'grant_type=urn:ibm:params:oauth:grant-type:apikey&apikey={}'.format(os.environ.get('APIKEY')).encode()
req = request.Request('https://iam.cloud.ibm.com/oidc/token', data = data)
req.add_header('Content-Type', 'application/x-www-form-urlencoded')
r = request.urlopen(req)
token = 'Bearer ' + json.loads(r.read())['access_token']

# configurations: disable facebook/google association
headers = {'Authorization': token, 'Content-Type': 'application/json'}

print(bcolors.OKGREEN + 'Starting to disable Facebook and Google identification association' + bcolors.ENDC)
def disableIDP(idp):
  req = request.Request(
    'https://{}.appid.cloud.ibm.com/management/v4/{}/config/idps/{}'.format(args.region, tenant_id, idp),
    data = data, method = 'PUT', headers = headers
  )
  with request.urlopen(req) as res:
    j = json.loads(res.read())
    if j['isActive'] is True:
      raise Exception('{} association is still active'.format(idp))

data = '{\"isActive\": false}'.encode()
disableIDP('facebook')
disableIDP('google')

# config cloud directory
# we have less security at MVP so that we don't accept for users to sign up on our app
print(bcolors.OKGREEN + 'Starting to configure the Cloud Directory' + bcolors.ENDC)
data = {
  'isActive': True,
  'config': {
    'selfServiceEnabled': True,
    'signupEnabled': False,
    'interactions': {
      'identityConfirmation': {
        'accessMode': args.email_confirmation,
        'methods': ['email']
      },
      'welcomeEnabled': False,
      'resetPasswordEnabled': False,
      'resetPasswordNotificationEnable': False
    },
    'identityField': 'email'
  }
}
data = json.dumps(data).encode()
req = request.Request(
  'https://{}.appid.cloud.ibm.com/management/v4/{}/config/idps/cloud_directory'.format(args.region, tenant_id),
  data = data, method = 'PUT', headers = headers
)
with request.urlopen(req) as res:
  if res.status != 200:
    raise Exception('Failed to add redirect URLs by {}'.format(res.reason))

# enable MFA
# FIXME: Multi-factor authentication can be enabled only on "Graduated tier" plan.
# use this API: /management/v4/{tenantId}/config/cloud_directory/mfa

# add customer logo
# we use cURL command instead of requests/urllib python libraries
# because the file upload request from python lib is not accepted by App ID.
# I tried it with several patterns of parameters but any didn't work.
print(bcolors.OKGREEN + 'Starting to upload the company logo' + bcolors.ENDC)

url = 'https://{}.appid.cloud.ibm.com/management/v4/{}/config/ui/media?mediaType=logo'.format(args.region, tenant_id)
command = ['curl', '-s', '-o', '/dev/null', '-w', '%{http_code}', '-X', 'POST', url]
command = command + ['-H', 'Authorization: {}'.format(token)]
command = command + ['-H', 'Content-Type: multipart/form-data']
command = command + ['-F', 'file=@{}'.format(args.logo_path)]
res = subprocess.check_output(command)
res = int(res.decode('utf-8'))
if res < 200 and res > 299:
  raise Exception('failed to upload company logo')

# add redirect URLs
print(bcolors.OKGREEN + 'Starting to add redirect URLs' + bcolors.ENDC)
urls = args.redirect_urls.split(',')
data = {'redirectUris': urls}
data = json.dumps(data).encode()
req = request.Request(
  'https://{}.appid.cloud.ibm.com/management/v4/{}/config/redirect_uris'.format(args.region, tenant_id),
  data = data, method = 'PUT', headers = headers
)
with request.urlopen(req) as res:
  if res.status != 204:
    raise Exception('Failed to add redirect URLs by {}'.format(res.reason))

# register your app and get credentials that includes secret, used by the client
print(bcolors.OKGREEN + 'Starting to register applicatinos' + bcolors.ENDC)
apps = args.application_names.split(',')
# check if there is a same app
req = request.Request(
  'https://{}.appid.cloud.ibm.com/management/v4/{}/applications'.format(args.region, tenant_id),
  headers = headers
)
with request.urlopen(req) as res:
  if res.status != 200:
    raise Exception('Failed to get existing apps by {}'.format(res.reason))
  existing_apps = json.loads(res.read())
# register apps
for i, app in enumerate(apps):
  if app not in [x['name'] for x in existing_apps['applications']]:
    print(bcolors.OKBLUE + 'registering ' + app + bcolors.ENDC)
    data = {'name': app}
    data = json.dumps(data).encode()
    req = request.Request(
      'https://{}.appid.cloud.ibm.com/management/v4/{}/applications'.format(args.region, tenant_id),
      data = data, method = 'POST', headers = headers
    )
    with request.urlopen(req) as res:
      if res.status != 200:
        raise Exception('Failed to add redirect URLs by {}'.format(res.reason))

      data = json.loads(res.read())
      print(json.dumps(data, indent=2))
      with open('.env.{}'.format(app), 'w') as f:
        f.write('''
        CLIENT_ID={}
        TENANT_ID={}
        SECRET={}
        OAUTH_SERVER_URL={}
        REDIRECT_URI={}
        '''.format(
          data['clientId'], data['tenantId'], data['secret'], data['oAuthServerUrl'], urls[i]
        ))

# add users
print(bcolors.OKGREEN + 'Starting to add users' + bcolors.ENDC)
users = [x.split(':') for x in args.application_users.split(',')]
# check if there is a same users
req = request.Request(
  'https://{}.appid.cloud.ibm.com/management/v4/{}/cloud_directory/Users'.format(args.region, tenant_id),
  headers = headers
)
with request.urlopen(req) as res:
  if res.status != 200:
    raise Exception('Failed to get existing apps by {}'.format(res.reason))
  existing_users = json.loads(res.read())
# add users
for user in users:
  if user[0] not in [x['displayName'] for x in existing_users['Resources']]:
    print(bcolors.OKBLUE + 'registering ' + user[0] + bcolors.ENDC)
    data = {
      'active': True,
      'emails': [{
        'value': user[0],
        'primary': True
      }],
      'userName': user[1],
      'password': user[2]
    }
    print(data)
    data = json.dumps(data).encode()
    req = request.Request(
      'https://{}.appid.cloud.ibm.com/management/v4/{}/cloud_directory/sign_up?shouldCreateProfile=true&language=en'.format(args.region, tenant_id),
      data = data, method = 'POST', headers = headers
    )
    with request.urlopen(req) as res:
      if res.status != 201:
        raise Exception('Failed to add redirect URLs by {}'.format(res.reason))

      data = json.loads(res.read())
      print(json.dumps(data, indent=2))
