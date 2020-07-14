#!/usr/bin/env python3

# reference:
# how to use HMAC: https://cloud.ibm.com/docs/cloud-object-storage/iam?topic=cloud-object-storage-uhc-hmac-credentials-main

import argparse
import subprocess
import sys
from os import path

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
create IBM Cloud Object Storage.
This requires an environment variable ${APIKEY} as your IAM API key.
""")
parser.add_argument(
  '-o', '--operation', default='create', help='create|delete a COS instance'
)
parser.add_argument(
  '-r', '--region', default='jp-tok', help='Region Name'
)
parser.add_argument(
  '-g', '--resource-group', default='c4c-covid-19', help='Resource Group Name'
)
parser.add_argument(
  '-n', '--instance-name', default='cos', help='Cloud Object Storage Instance Name'
)
parser.add_argument(
  '-p', '--service-plan', default='lite', help='Service Plan Name'
)
parser.add_argument(
  '-b', '--buckets', default='covsafe',
  help='Comma-Separated bucket name list'
)
parser.add_argument(
  '-d', '--data', help='''
  Comma-n-Semicolon-Separated list that has files uploaded.
  The each item should be format of FILEPATH;BUCKET so that this list could be
  FILEPATH1;BUCKET1,FILEPATH2:BUCKET2.
  '''
)
parser.add_argument('-k', '--keyname', help='Key name for HMAC Credentials')

args = parser.parse_args()

def create():
  # create IBM Cloud Object Storage
  print(bcolors.OKGREEN + 'Starting to create a Cloud Object Storage' + bcolors.ENDC)
  # check if an instacne is
  p1 = subprocess.Popen(['ibmcloud', 'resource', 'service-instances'], stdout=subprocess.PIPE)
  p2 = subprocess.Popen(['grep', args.instance_name], stdin=p1.stdout, stdout=subprocess.PIPE)
  p3 = subprocess.Popen(['wc', '-l'], stdin=p2.stdout, stdout=subprocess.PIPE)
  res = p3.communicate()[0]

  if int(res.decode('utf-8')) == 0:
    # create an instance
    subprocess.check_call(
      ['ibmcloud', 'resource', 'service-instance-create',
      args.instance_name, 'cloud-object-storage', args.service_plan, 'global']
    )

  # get tenant ID of COS
  p1 = subprocess.Popen(['ibmcloud', 'resource', 'service-instance', args.instance_name], stdout=subprocess.PIPE)
  p2 = subprocess.Popen(['awk', '-F:', '/^ID/ {print $9}'], stdin=p1.stdout, stdout=subprocess.PIPE)
  tenant_id = p2.communicate()[0].decode('utf-8').strip()

  # switch to auth IAM
  p1 = subprocess.Popen(['ibmcloud', 'cos', 'config', 'auth', '--method', 'IAM'], stdout=subprocess.PIPE)
  wait = p1.communicate()
  print(wait[0].decode('utf-8'))
  if p1.returncode != 0:
    print(bcolors.FAIL + 'cannot switch to IAM auth' + bcolors.ENDC)
    sys.exit(1)

  # create buckets
  buckets = args.buckets.split(',')
  for bucket in buckets:
    # check if the bucket is
    p1 = subprocess.Popen([
        'ibmcloud', 'cos', 'get-bucket-location', '--bucket', bucket
    ], stdout=subprocess.PIPE)
    wait = p1.communicate()

    # create a bucket
    if p1.returncode != 0:
      p1 = subprocess.Popen([
        'ibmcloud', 'cos', 'create-bucket', '--bucket', bucket,
        '--ibm-service-instance-id', tenant_id, '--region', args.region], stdout=subprocess.PIPE)
      print(p1.communicate()[0].decode('utf-8'))
      if p1.returncode != 0:
        print(bcolors.FAIL + 'cannot create bucket {}'.format(bucket) + bcolors.ENDC)
        sys.exit(1)

  # upload files
  data = args.data.split(',')
  for d in data:
    f, bucket = d.split(';')
    if path.exists(f) is True:
      p1 = subprocess.Popen([
        'ibmcloud', 'cos', 'put-object', '--bucket', bucket, '--key', path.basename(f),
        '--body', f, '--region', args.region
      ], stdout=subprocess.PIPE)
      wait = p1.communicate()
      
      if p1.returncode != 0:
        print(bcolors.FAIL + 'cannot upload data {} due to {}'.format(f, wait[0]) + bcolors.ENDC)
      else:
        print(wait[0].decode('utf-8'))
    else:
      print(bcolors.FAIL + 'there is no data {}'.format(f) + bcolors.ENDC)

  # generate HMAC credentials
  p1 = subprocess.Popen(['ibmcloud', 'resource', 'service-keys'], stdout=subprocess.PIPE)
  p2 = subprocess.Popen(['grep', args.keyname], stdin=p1.stdout, stdout=subprocess.PIPE)
  wait = p2.communicate()
  if p2.returncode != 0:
    p1 = subprocess.Popen([
      'ibmcloud', 'resource', 'service-key-create', args.keyname,
      'Reader', '--instance-name', 'cos', '--parameters', '{"HMAC":true}'], stdout=subprocess.PIPE)
    p2 = subprocess.Popen([
      'awk', '-F:', '/(access_key_id|secret_access_key)/ {print $2}'
    ], stdin=p1.stdout, stdout=subprocess.PIPE)
    wait = p2.communicate()
    if p2.returncode == 0:
      lines = wait[0].decode('utf-8').split('\n')
      print(bcolors.OKBLUE + 'COS_HMAC_ACCESS_KEY_ID={}'.format(lines[0]) + bcolors.ENDC)
      print(bcolors.OKBLUE + 'COS_HMAC_SECRET_ACCESS_KEY={}'.format(lines[1]) + bcolors.ENDC)
      with open('./.env-cos-hmac', 'w') as f:
        f.write('COS_HMAC_ACCESS_KEY_ID={}\n'.format(lines[0].strip()))
        f.write('COS_HMAC_SECRET_ACCESS_KEY={}\n'.format(lines[1].strip()))
    else:
      print(bcolors.FAIL + 'cannot create hmac keys' + bcolors.ENDC)
      sys.exit(1)

  # switch back to auth HMAC
  p1 = subprocess.Popen(['ibmcloud', 'cos', 'config', 'auth', '--method', 'HMAC'], stdout=subprocess.PIPE)
  wait = p1.communicate()
  print(wait[0].decode('utf-8'))
  if p1.returncode != 0:
    print(bcolors.FAIL + 'cannot switch to HMAC auth' + bcolors.ENDC)
    sys.exit(1)  

def delete():
  # create IBM Cloud Object Storage
  print(bcolors.OKGREEN + 'Starting to delete a Cloud Object Storage' + bcolors.ENDC)
  # check if it is, and get tenant id
  p1 = subprocess.Popen(['ibmcloud', 'resource', 'service-instance', args.instance_name], stdout=subprocess.PIPE)
  p2 = subprocess.Popen(['awk', '-F:', '/^ID/ {print $9}'], stdin=p1.stdout, stdout=subprocess.PIPE)
  wait = p2.communicate()
  if len(wait[0]) == 0:
    print(bcolors.FAIL + 'no instance {}'.format(args.instance_name) + bcolors.ENDC)
    sys.exit(1)

  # delete an instance
  p1 = subprocess.Popen([
    'ibmcloud', 'resource', 'service-instance-delete', args.instance_name,
    '-g', args.resource_group, '--force', '--recursive'
  ], stdout=subprocess.PIPE)
  print(p1.communicate()[0].decode('utf-8'))


if args.operation == 'create':
  create()
elif args.operation == 'delete':
  delete()
else:
  print(bcolors.WARNING + 'no option. please check usage of this script.' + bcolors.ENDC)
