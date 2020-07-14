#!/usr/bin/env python3

import argparse
import subprocess
import sys
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
create IBM Cloud Object Storage.
This requires an environment variable ${APIKEY} as your IAM API key.
""")
parser.add_argument('-b', '--bucket', help='Bucket name')
parser.add_argument('-k', '--key', help='Key name')
parser.add_argument('-r', '--region', default='jp-tok', help='Region Name')
parser.add_argument('-g', '--resource-group', default='c4c-covid-19', help='Resource Group Name')

args = parser.parse_args()

# create IBM Cloud Object Storage
print(bcolors.OKGREEN + 'Starting to get an object' + bcolors.ENDC)
# [--region REGION] [--json] [OUTFILE]
p1 = subprocess.Popen([
  'ibmcloud', 'cos', 'get-object', '--bucket', args.bucket, '--key', args.key,
  '--region', args.region
], stdout=subprocess.PIPE)
print(p1.communicate())
print(p1.returncode)
