#!/usr/bin/env python3

import argparse
import os
import sys
import uuid
import util
import service_app_id as app_id
import service_cos as cos
import service_cloudant as nosql
import service_event_streams as es

CREDENTIALS_FILE = './.credentials'
COVSAFE_VIEW = 'covsafe-view'
ES_TOPICS = 'covsafe'
APPID_REGISTERED_APP = 'covsafe'
APPID_REGISTERED_USER = 'user@fake.email:JamesSmith:password'
UI_COMPONENTS_BUCKET = 'UI_COMPONENTS_BUCKET'
CLOUDANT_DB = 'assets,assets_staff,view-config,log_risk_calculation,log_risk_notifier,a_notification_template,ads,shops'
SERVICES = {
  'app_id': 'app-id',
  'cos': 'cos',
  'cloudant': 'cloudant',
  'event_streams': 'es'
}

# get arguments
def parse_args(args):
  parser = argparse.ArgumentParser(description="""
  deploy covsafe solution to IBM Cloud.
  This requires an environment variable ${APIKEY} as your IAM API key.
  """)
  parser.add_argument('-o', '--operation', default='create', help='create|delete the solution')
  parser.add_argument('-p', '--project', default='covsafe', help='Project Name')
  parser.add_argument(
    '-t', '--tenant', default='c4c', help='''
    Tenant ID to select data set. This should be one of dir name under /path/to/project/data/'
    '''
  )
  parser.add_argument('-r', '--region', default='jp-tok', help='Region Name')
  parser.add_argument('-g', '--resource-group', default='c4c-covid-19', help='Resource Group Name')

  return parser.parse_args(args)

def create(args):
  init()
  args = parse_args(args)

  util.login(args.region, args.resource_group)

  # create UI namespace for app ID
  util.create_functions_namespace(COVSAFE_VIEW)
  view_ns = util.get_functions_namespace_id(COVSAFE_VIEW)
  view_api = 'https://{}.functions.appdomain.cloud/api/v1/web/{}/covsafe/view'.format(args.region, view_ns)

  # create IBM Event Streams
  es.create([
    '-r', args.region, '-g', args.resource_group, '-p', 'lite', '-n', SERVICES['event_streams'],
    '-k', 'event-streams-key', '-c', CREDENTIALS_FILE, '-t', ES_TOPICS
  ])

  # create IBM Cloud Cloudant
  # FIXME: might need to create index to avoid the query error
  data = [
    '../data/common/cloudant/notification-template.json;a_notification_template',
    '../data/common/cloudant/view-config.json;view-config',
    '../data/{}/cloudant/assets.json;assets'.format(args.tenant),
    '../data/{}/cloudant/assets_staff.json;assets_staff'.format(args.tenant),
    '../data/{}/cloudant/shops.json;shops'.format(args.tenant)
  ]
  nosql.create([
    '-r', args.region, '-g', args.resource_group, '-p', 'lite', '-n', SERVICES['cloudant'],
    '-k', 'cloudant-key', '-c', CREDENTIALS_FILE, '-b', CLOUDANT_DB,
    '-d', ','.join(data)
  ])

  # create IBM Cloud Object Storage
  bucket = util.get_credentials_value(CREDENTIALS_FILE, UI_COMPONENTS_BUCKET)
  cosdir = '../data/tenants/{}/cos'.format(args.tenant)
  files = [f for f in os.listdir(cosdir) if os.path.isfile(os.path.join(cosdir, f))]
  data = ','.join(['{};{}'.format(x, bucket) for x in files])

  cos.create([
    '-r', args.region, '-g', args.resource_group, '-p', 'lite', '-n', SERVICES['cos'],
    '-k', 'cos-hmac', '-c', CREDENTIALS_FILE, '-b', bucket, '-d', data
  ])

  # create IBM App ID
  # should be later than deployment of UI, because it requires redirect URL
  app_id.create([
    '-r', args.region, '-g', args.resource_group, '-p', 'lite', '-n', SERVICES['app_id'],
    '-e', 'OFF', '-u', view_api, '-a', APPID_REGISTERD_APP,
    '-s', 'user@fake.email:JamesSmith:password'
  ])

  post_create()

def delete(args):
  args = parse_args(args)
  app_id.delete(['-n', SERVICES['app_id'], '-g', args.resource_group])

  bucket = util.get_credentials_value(CREDENTIALS_FILE, UI_COMPONENTS_BUCKET)
  cosdir = './data/tenants/{}/cos'.format(args.tenant)
  files = [f for f in os.listdir(cosdir) if os.path.isfile(os.path.join(cosdir, f))]
  data = ','.join(['{};{}'.format(x, bucket) for x in files])
  cos.delete([
    '-n', SERVICES['cos'], '-g', args.resource_group, '-r', args.region,
    '-b', bucket, '-d', data
  ])
  nosql.delete(['-n', SERVICES['cloudant'], '-g', args.resource_group])
  es.create(['-n', SERVICES['event_streams'], '-g', args.resource_group])
  util.create_functions_namespace(COVSAFE_VIEW)
  post_delete()

def init():
  with open(CREDENTIALS_FILE, 'w') as f:
    f.write('{}={}\n'.format(UI_COMPONENTS_BUCKET, str(uuid.uuid4())))

def post_create():
  print('shomething new')

def post_delete():
  os.remove(CREDENTIALS_FILE)


if __name__ == '__main__':
  args = parse_args(sys.argv[1:])
  if args.operation == 'create':
    create(sys.argv[1:])
  elif args.operation == 'delete':
    delete(sys.argv[1:])
  else:
    print(util.bcolors.WARNING + 'no option. please check usage of this script.' + util.bcolors.ENDC)
