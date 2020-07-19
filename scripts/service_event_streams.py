import argparse
import subprocess
import json
import sys
from os import path
import util


# get arguments
def parse_args(args):
  parser = argparse.ArgumentParser(description="""
  create IBM Cloud Cloudant.
  """)
  parser.add_argument('-o', '--operation', default='create', help='create|delete a instance')
  parser.add_argument('-r', '--region', default='jp-tok', help='region Name')
  parser.add_argument('-g', '--resource-group', default='c4c-covid-19', help='resource group name')
  parser.add_argument('-n', '--instance-name', default='cloudantnodqldb', help='instance name')
  parser.add_argument('-p', '--service-plan', default='lite',
    help='service plan (lite|standard|enterprise)')
  parser.add_argument('-k', '--keyname-prefix', default='cloudant-key',
    help='prefix of service credentials key')
  parser.add_argument('-c', '--credential-file', default='./.credentials',
    help='file path to store the service credentials')
  parser.add_argument('-t', '--topics', help='comma-separated list of topic names')

  return parser.parse_args(args)

def create(args):
  args = parse_args(args)

  util.create_service_instance(args.instance_name, 'messagehub', args.service_plan, args.region)

  wcred = util.create_service_credential(args.keyname_prefix, 'Writer', args.instance_name)
  rcred = util.create_service_credential(args.keyname_prefix, 'Reader', args.instance_name)
  with open(args.credential_file, 'a') as f:
    f.write('EVENT_STREAMS_WRITER_CREDENTIALS={}\n'.format(json.dumps(wcred[0]['credentials'])))
    f.write('EVENT_STREAMS_READER_CREDENTIALS={}\n'.format(json.dumps(rcred[0]['credentials'])))

  # w and r has same admin url
  util.event_streams_init(args.instance_name, wcred[0]['credentials']['kafka_admin_url'])

  util.create_topic(args.topics.split(','))

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
