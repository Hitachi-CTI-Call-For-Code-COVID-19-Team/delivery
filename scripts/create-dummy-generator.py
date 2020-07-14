#!/usr/bin/env python3

import argparse
import subprocess
import os
import sys

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
deploy dummy generator onto IBM Cloud Functions.
This requires an environment variable ${APIKEY} as your IAM API key.
""")
parser.add_argument('-o', '--operation', default='create', help='create|delete a dummy-generator')
parser.add_argument('-r', '--region', default='jp-tok', help='Region Name')
parser.add_argument('-g', '--resource-group', default='c4c-covid-19', help='Resource Group Name')
parser.add_argument('-n', '--namespace', default='dummy-generator', help='Namespace name for generator')
parser.add_argument('-p', '--package', default='dummy-generator', help='Package name for generator')
parser.add_argument('-a', '--action', default='dummy-generator', help='Action name for generator')
parser.add_argument('-f', '--file', default='./functions/dummy-generator.js', help='source code for generator')

args = parser.parse_args()

# login and set target region and resource group
print(bcolors.OKGREEN + 'Login to IBM Cloud' + bcolors.ENDC)
subprocess.check_call(['ibmcloud', 'login', '--apikey', os.environ.get('APIKEY')])
subprocess.check_call(['ibmcloud', 'target', '-r', args.region, '-g', args.resource_group])

def create():
  # create and set namespace
  p1 = subprocess.Popen(['ibmcloud', 'fn', 'namespace', 'list'], stdout=subprocess.PIPE)
  p2 = subprocess.Popen(['grep', args.namespace], stdin=p1.stdout, stdout=subprocess.PIPE)
  wait = p2.communicate()
  if p2.returncode != 0:
    p1 = subprocess.Popen(['ibmcloud', 'fn', 'namespace', 'create', args.namespace], stdout=subprocess.PIPE)
    wait = p1.communicate()
    print(wait[0].decode('utf-8'))
    if p1.returncode != 0:
      print(bcolors.FAIL + 'cannot create namespace {}'.format(args.namespace) + bcolors.ENDC)
      sys.exit(1)

  p1 = subprocess.Popen(['ibmcloud', 'fn', 'property', 'set', '--namespace', args.namespace], stdout=subprocess.PIPE)
  print(p1.communicate()[0].decode('utf-8'))

  # create package
  p1 = subprocess.Popen(['ibmcloud', 'fn', 'package', 'list'], stdout=subprocess.PIPE)
  p2 = subprocess.Popen(['grep', args.package], stdin=p1.stdout, stdout=subprocess.PIPE)
  wait = p2.communicate()
  if p2.returncode != 0:
    p1 = subprocess.Popen(['ibmcloud', 'fn', 'package', 'create', args.package], stdout=subprocess.PIPE)
    wait = p1.communicate()
    print(wait[0].decode('utf-8'))
    if p1.returncode != 0:
      print(bcolors.FAIL + 'cannot create package {}'.format(args.package) + bcolors.ENDC)
      sys.exit(1)

  # create action
  p1 = subprocess.Popen(['ibmcloud', 'fn', 'action', 'list'], stdout=subprocess.PIPE)
  p2 = subprocess.Popen([
    'grep', '{}/{}'.format(args.package, args.action)
  ], stdin=p1.stdout, stdout=subprocess.PIPE)
  wait = p2.communicate()

  p1 = subprocess.Popen([
    'ibmcloud', 'fn', 'action', 'create' if p1.returncode == 0 else 'update',
    '{}/{}'.format(args.package, args.action), args.file
  ], stdout=subprocess.PIPE)
  wait = p1.communicate()
  print(wait[0].decode('utf-8'))
  if p1.returncode != 0:
    print(bcolors.FAIL + 'cannot create/update action {}/{}'.format(args.package, args.action) + bcolors.ENDC)
    sys.exit(1)


def delete():
  p1 = subprocess.Popen([
    'ibmcloud', 'fn', 'action', 'delete', '{}/{}'.format(args.package, args.action)
  ], stdout=subprocess.PIPE)
  print(p1.communicate()[0].decode('utf-8'))
  p1 = subprocess.Popen(['ibmcloud', 'fn', 'package', 'delete', args.package], stdout=subprocess.PIPE)
  print(p1.communicate()[0].decode('utf-8'))
  p1 = subprocess.Popen(['ibmcloud', 'fn', 'namespace', 'delete', args.namespace], stdout=subprocess.PIPE)
  print(p1.communicate()[0].decode('utf-8'))

if args.operation == 'create':
  create()
elif args.operation == 'delete':
  delete()
else:
  print(bcolors.WARNING + 'no option. please check usage of this script.' + bcolors.ENDC)
