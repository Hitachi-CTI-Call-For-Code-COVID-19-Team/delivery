#!/usr/bin/env python3

# Reference:
# [IBM Cloud App ID API list](https://us-south.appid.cloud.ibm.com/swagger-ui/#/)

import argparse
import subprocess
import os
import json
from urllib import request
import util


# get arguments
def parse_args(args):
  parser = argparse.ArgumentParser(description="""
  create IBM Cloud App ID instance.
  """)
  parser.add_argument('-o', '--operation', default='create', help='create|delete the solution')
  parser.add_argument('-r', '--region', default='jp-tok', help='region name')
  parser.add_argument('-g', '--resource-group', default='c4c-covid-19', help='resource group name')
  parser.add_argument('-p', '--service-plan', default='lite', help='service plan name')
  parser.add_argument('-n', '--instance-name', default='app-id', help='App ID instance name')
  parser.add_argument('-l', '--logo-path',
    help='path to logo file used in login page. relative path is acceptable'
  )
  parser.add_argument('-e', '--email-confirmation', default='OFF',
    help='''
    FULL|OFF.
    FULL means to verify email address given by signing up.
    OFF doesn't require email verification.
    '''
  )
  parser.add_argument(
    '-u', '--redirect-urls', default='http://localhost:8080/callback',
    help='''
    comma-separated redirect url list.
    these should be URLs called back from App ID.
    note that it should not be '/' which causes ERR_TOO_MANY_REDIRECTS.
    '''
  )
  parser.add_argument(
    '-a', '--application-names', default='covsafe-view',
    help='''
    comma-separaqted application names registered to App ID.
    note that redirect URLs in the redirect-urls should be the URLs of this app,
    which are in the same order.
    '''
  )
  parser.add_argument(
    '-s', '--application-users',
    default='user@fake.email:JamesSmith:password',
    help='''
    comma-and-colon-separated user list.
    each user should be colon-separated attribute list with EMAIL:USERNAME:PASSWORD.
    '''
  )
  parser.add_argument(
    '-c', '--credential-file', default='./.credentials', help='file path to store the service credentials'
  )

  return parser.parse_args(args)

def create(args):
  args = parse_args(args)

  util.create_service_instance(args.instance_name, 'appid', args.service_plan, args.region)

  tenant_id = util.get_tenant_id(args.instance_name)

  token = util.get_IAM_token()
  headers = {'Authorization': token, 'Content-Type': 'application/json'}

  # configurations: disable facebook/google association
  print(
    util.bcolors.OKGREEN +
    'Starting to disable Facebook and Google identification association' +
    util.bcolors.ENDC
  )

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
  print(util.bcolors.OKGREEN + 'Starting to configure the Cloud Directory' + util.bcolors.ENDC)
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
    'https://{}.appid.cloud.ibm.com/management/v4/{}/config/idps/cloud_directory'.format(
      args.region, tenant_id
    ),
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
  if args.logo_path is not None:
    print(util.bcolors.OKGREEN + 'Starting to upload the company logo' + util.bcolors.ENDC)

    url = 'https://{}.appid.cloud.ibm.com/management/v4/{}/config/ui/media?mediaType=logo'.format(
      args.region, tenant_id
    )
    command = ['curl', '-s', '-o', '/dev/null', '-w', '%{http_code}', '-X', 'POST', url]
    command = command + ['-H', 'Authorization: {}'.format(token)]
    command = command + ['-H', 'Content-Type: multipart/form-data']
    command = command + ['-F', 'file=@{}'.format(args.logo_path)]
    res = subprocess.check_output(command)
    res = int(res.decode('utf-8'))
    if res < 200 and res > 299:
      raise Exception('failed to upload company logo')

  # add redirect URLs
  print(util.bcolors.OKGREEN + 'Starting to add redirect URLs' + util.bcolors.ENDC)
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
  print(util.bcolors.OKGREEN + 'Starting to register applicatinos' + util.bcolors.ENDC)
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
      print(util.bcolors.OKBLUE + 'registering ' + app + util.bcolors.ENDC)
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
        prefix = app.upper().replace('-', '_')
        with open(args.credential_file, 'a') as f:
          f.write('{}_CLIENT_ID={}\n'.format(prefix, data['clientId']))
          f.write('{}_TENANT_ID={}\n'.format(prefix, data['tenantId']))
          f.write('{}_SECRET={}\n'.format(prefix, data['secret']))
          f.write('{}_OAUTH_SERVER_URL={}\n'.format(prefix, data['oAuthServerUrl']))
          f.write('{}_REDIRECT_URI={}\n'.format(prefix, urls[i]))

  # add users
  print(util.bcolors.OKGREEN + 'Starting to add users' + util.bcolors.ENDC)
  users = [x.split(':') for x in args.application_users.split(',')]
  # check if there is a same users
  req = request.Request(
    'https://{}.appid.cloud.ibm.com/management/v4/{}/cloud_directory/Users'.format(
      args.region, tenant_id
    ),
    headers = headers
  )
  with request.urlopen(req) as res:
    if res.status != 200:
      raise Exception('Failed to get existing apps by {}'.format(res.reason))
    existing_users = json.loads(res.read())
  # add users
  for user in users:
    if user[0] not in [x['displayName'] for x in existing_users['Resources']]:
      print(util.bcolors.OKBLUE + 'registering ' + user[0] + util.bcolors.ENDC)
      data = {
        'active': True,
        'emails': [{
          'value': user[0],
          'primary': True
        }],
        'userName': user[1],
        'password': user[2]
      }
      data = json.dumps(data).encode()
      req = request.Request(
        'https://{}.appid.cloud.ibm.com/management/v4/{}/cloud_directory/sign_up?shouldCreateProfile=true&language=en'.format(args.region, tenant_id),
        data = data, method = 'POST', headers = headers
      )
      with request.urlopen(req) as res:
        if res.status != 201:
          raise Exception('Failed to add redirect URLs by {}'.format(res.reason))

        data = json.loads(res.read())

def delete(args):
  args = parse_args(args)
  util.delete_service_instance(args.instance_name, args.resource_group)


if __name__ == '__main__':
  args = parse_args(sys.argv[1:])
  if args.operation == 'create':
    create(sys.argv[1:])
  elif args.operation == 'delete':
    delete(sys.argv[1:])
  else:
    print(util.bcolors.WARNING + 'no option. please check usage of this script.' + util.bcolors.ENDC)
