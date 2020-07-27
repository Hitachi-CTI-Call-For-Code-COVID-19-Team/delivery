#!/usr/bin/env python3

import argparse
import subprocess
import os
import sys
import json
import util


def parse_args(args):
  parser = argparse.ArgumentParser(description="""
  deploy dummy generator onto IBM Cloud Functions.
  This requires an environment variable ${APIKEY} as your IAM API key.
  """)
  parser.add_argument('-o', '--operation', default='create', help='create|delete a dummy-generator')
  parser.add_argument('-r', '--region', default='jp-tok', help='region name')
  parser.add_argument('-g', '--resource-group', default='c4c-covid-19', help='resource Group Name')
  parser.add_argument('-n', '--namespaces',
    default='covsafe-view,reader,risk-calculation-notification,data-recorder',
    help='comma-separated namespaces'
  )
  parser.add_argument('-f', '--file', default='./.namespaces', help='temporal file to store namespaces')

  return parser.parse_args(args)


def create(args):
  args = parse_args(args)

  util.login(args.region, args.resource_group)

  namespaces = args.namespaces.split(',')
  for ns in namespaces:
    util.create_functions_namespace(ns)
    id = util.get_functions_namespace_id(ns)
    with open(args.file, 'w') as f:
      f.write('{}={}\n'.format(ns, id))


def delete(args):
  args = parse_args(args)

  util.login(args.region, args.resource_group)

  namespaces = args.namespaces.split(',')
  for ns in namespaces:
    util.delete_functions_namespace(ns)
  
  os.remove(args.file)


if __name__ == '__main__':
  args = parse_args(sys.argv[1:])
  if args.operation == 'create':
    create(sys.argv[1:])
  elif args.operation == 'delete':
    delete(sys.argv[1:])
  else:
    print(util.bcolors.WARNING + 'no option. please check usage of this script.' + util.bcolors.ENDC)
