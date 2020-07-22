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
UI_COMPONENTS_BUCKET = 'UI_COMPONENTS_BUCKET'
COVSAFE_VIEW_REDIRECT_URL = 'COVSAFE_VIEW_REDIRECT_URL'
ASSETS_DB = 'assets'
SERVICES = {
  'app_id': 'app-id',
  'cos': 'cos',
  'cloudant': 'cloudant-dev',
  'event_streams': 'Event Streams'
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

  # create IBM Event Streams
  es.create([
    '-r', args.region, '-g', args.resource_group, '-p', 'lite', '-n', SERVICES['event_streams'],
    '-k', 'event-streams-key', '-c', CREDENTIALS_FILE, '-t', 'covsafe'
  ])

  # create IBM Cloud Cloudant
  nosql.create([
    '-r', args.region, '-g', args.resource_group, '-p', 'lite', '-n', SERVICES['cloudant'],
    '-k', 'cloudant-key', '-c', CREDENTIALS_FILE, '-b', ASSETS_DB,
    '-d', '../data/{}/assets.json;{}'.format(args.tenant, ASSETS_DB)
  ])

  # create IBM Cloud Object Storage
  bucket = util.get_credentials_value(CREDENTIALS_FILE, UI_COMPONENTS_BUCKET)
  cos.create([
    '-r', args.region, '-g', args.resource_group, '-p', 'lite', '-n', SERVICES['cos'],
    '-b', bucket,
    '-d', '../data/{}/floormap.png;{}'.format(args.tenant, bucket),
    '-k', 'cos-hmac', '-c', CREDENTIALS_FILE
  ])

  # create IBM App ID
  # should be later than deployment of UI, because it requires redirect URL
  redirect_url = util.get_credentials_value(CREDENTIALS_FILE, COVSAFE_VIEW_REDIRECT_URL)
  app_id.create([
    '-r', args.region, '-g', args.resource_group, '-p', 'lite', '-n', SERVICES['app_id'],
    '-e', 'OFF', '-u', redirect_url, '-a', 'covsafe-view',
    '-s', 'user@fake.email:JamesSmith:password'
  ])

  post_create()

def delete(args):
  args = parse_args(args)
  app_id.delete(['-n', SERVICES['app_id'], '-g', args.resource_group])
  bucket = util.get_credentials_value(CREDENTIALS_FILE, UI_COMPONENTS_BUCKET)
  cos.delete([
    '-n', SERVICES['cos'], '-g', args.resource_group, '-r', args.region,
    '-b', bucket,
    '-d', '../data/{}/floormap.png;{}'.format(args.tenant, bucket)
  ])
  # nosql.delete(['-n', SERVICES['cloudant'], '-g', args.resource_group])
  # es.create(['-n', SERVICES['event_streams'], '-g', args.resource_group])
  post_delete()

def init():
  with open(CREDENTIALS_FILE, 'w') as f:
    f.write('{}={}\n'.format(UI_COMPONENTS_BUCKET, str(uuid.uuid4())))
    f.write('{}={}\n'.format(COVSAFE_VIEW_REDIRECT_URL, 'http://localhost:8080/callback'))

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
