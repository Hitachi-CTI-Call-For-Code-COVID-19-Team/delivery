#!/usr/bin/env python3

# reference:
# how to use HMAC: https://cloud.ibm.com/docs/cloud-object-storage/iam?topic=cloud-object-storage-uhc-hmac-credentials-main

import argparse
import subprocess
import sys
import json
from os import path
import util

# get arguments
def parse_args(args):
  parser = argparse.ArgumentParser(description="""
  create IBM Cloud Object Storage.
  This requires an environment variable ${APIKEY} as your IAM API key.
  """)
  parser.add_argument('-o', '--operation', default='create', help='create|delete a COS instance')
  parser.add_argument('-r', '--region', default='jp-tok', help='region name')
  parser.add_argument('-g', '--resource-group', default='c4c-covid-19', help='resource group name')
  parser.add_argument('-n', '--instance-name', default='cos', help='cloud object storage instance name')
  parser.add_argument('-p', '--service-plan', default='lite', help='service plan name')
  parser.add_argument('-b', '--buckets', help='comma-separated bucket name list')
  parser.add_argument(
    '-d', '--data', help='''
    comma-n-semicolon-separated list that has files uploaded.
    The each item should be format of FILEPATH;BUCKET so that this list could be
    FILEPATH1;BUCKET1,FILEPATH2:BUCKET2.
    '''
  )
  parser.add_argument(
    '-k', '--keyname-prefix', default='cos-hmac', help='prefix of HMAC credentials'
  )
  parser.add_argument(
    '-c', '--credential-file', default='./.credentials', help='file path to store the service credentials'
  )

  return parser.parse_args(args)

def create(args):
  args = parse_args(args)

  util.create_service_instance(args.instance_name, 'cloud-object-storage', args.service_plan, 'global')

  tenant_id = util.get_tenant_id(args.instance_name)

  switch_auth('IAM')

  util.create_buckets(args.buckets.split(','), args.region, tenant_id)

  util.put_objects([x.split(';') for x in args.data.split(',')], args.region)

  # generate HMAC credentials
  for role in ['Reader', 'Writer']:
    cred = util.create_service_credential(
      args.keyname_prefix, role, args.instance_name, '--parameters', '{"HMAC":true}'
    )

    with open(args.credential_file, 'a') as f:
      f.write('COS_{}_CREDENTIALS={}\n'.format(role.upper(), json.dumps(cred[0]['credentials'])))

  switch_auth('HMAC')

def delete(args):
  args = parse_args(args)
  switch_auth('IAM')
  util.delete_objects([x.split(';') for x in args.data.split(',')], args.region)
  util.delete_buckets(args.buckets.split(','), args.region)
  util.delete_service_instance(args.instance_name, args.resource_group)

def switch_auth(method):
  print(util.bcolors.OKGREEN + 'Switch auth method to {}'.format(method) + util.bcolors.ENDC)

  p1 = subprocess.Popen(['ibmcloud', 'cos', 'config', 'auth', '--method', method],
    stdout=subprocess.PIPE)
  wait = p1.communicate()
  if p1.returncode != 0:
    print(util.bcolors.FAIL + 'cannot switch to auth method' + util.bcolors.ENDC)
    raise Exception('cannot switch to auth method')


if __name__ == '__main__':
  args = parse_args(sys.argv[1:])
  if args.operation == 'create':
    create(sys.argv[1:])
  elif args.operation == 'delete':
    delete(sys.argv[1:])
  else:
    print(util.bcolors.WARNING + 'no option. please check usage of this script.' + util.bcolors.ENDC)
