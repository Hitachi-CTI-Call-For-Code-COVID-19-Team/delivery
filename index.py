#!/usr/bin/env python3

import argparse
import subprocess
import os

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
deploy covsafe solution to IBM Cloud.
This requires an environment variable ${APIKEY} as your IAM API key.
""")
parser.add_argument(
  '-p', '--project', default='covsafe', help='Project Name'
)
parser.add_argument(
  '-t', '--tenant', default='c4c', help='''
  Tenant ID to select data set. This should be one of dir name under /path/to/project/data/'
  '''
)
parser.add_argument(
  '-r', '--region', default='jp-tok', help='Region Name'
)
parser.add_argument(
  '-g', '--resource-group', default='c4c-covid-19', help='Resource Group Name'
)

args = parser.parse_args()

# login and set target region and resource group
print(bcolors.OKGREEN + 'Login to IBM Cloud' + bcolors.ENDC)
subprocess.check_call(
  ['ibmcloud', 'login', '--apikey', os.environ.get('APIKEY')])
subprocess.check_call(
  ['ibmcloud', 'target', '-r', args.region, '-g', args.resource_group])


# create IBM Cloud Object Storage
bucket = '{}-{}-ui-components'.format(args.project, args.tenant)
subprocess.check_call([
  'python3', './scripts/cos.py', '-r', args.region, '-g', args.resource_group,
  '-n', 'cos', '-p', 'lite', '-b', bucket,
  '-d', './data/{}/floormap.png;{}'.format(args.tenant, bucket),
  '-k', '{}-{}-cos-read-key'.format(args.project, args.tenant)
])
