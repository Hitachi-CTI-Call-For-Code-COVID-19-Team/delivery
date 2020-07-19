import argparse
import subprocess
import json
import sys
import re
from os import path
from cloudant.client import Cloudant
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
  parser.add_argument('-p', '--service-plan', default='lite', help='service plan (lite|standard)')
  parser.add_argument('-k', '--keyname-prefix', default='cloudant-key',
    help='prefix of service credentials key')
  parser.add_argument('-c', '--credential-file', default='./.credentials',
    help='file path to store the service credentials')
  parser.add_argument('-b', '--database', help='comma-separated list of database created')
  parser.add_argument('-d', '--data',
    help='comma-and-colon-separated list that has files uploaded. it should FILE1;DB1,FILE2;DB2')

  return parser.parse_args(args)

def create(args):
  args = parse_args(args)

  util.create_service_instance(args.instance_name, 'cloudantnosqldb', args.service_plan, args.region)

  wcred = util.create_service_credential(
    args.keyname_prefix, 'Writer', args.instance_name
  )
  rcred = util.create_service_credential(
    args.keyname_prefix, 'Reader', args.instance_name
  )
  with open(args.credential_file, 'a') as f:
    f.write('CLOUDANT_WRITER_CREDENTIALS={}\n'.format(json.dumps(wcred[0]['credentials'])))
    f.write('CLOUDANT_READER_CREDENTIALS={}\n'.format(json.dumps(rcred[0]['credentials'])))

  # write data
  if args.database is not None and args.data is not None:

    # get each from credentials
    url = wcred[0]['credentials']['url']
    m = re.match('https://(.*):(.*)@(.*)$', url)
    sc_username = m.group(1)
    sc_password = m.group(2)
    sc_url = 'https://{}'.format(m.group(3))

    # create client
    client = Cloudant(sc_username, sc_password, url=sc_url)
    client.connect()

    # create database
    databases = args.database.split(',')
    for database in databases:
      db = client.create_database(database)
      if db.exists():
        print(util.bcolors.OKBLUE + 'created {}'.format(database) + util.bcolors.ENDC)
      else:
        print(util.bcolors.FAIL + 'failed to create database {}'.format(database) + util.bcolors.ENDC)
        raise Exception('failed to create database {}'.format(database))

    # write data
    units = args.data.split(',')
    for unit in units:
      file, dababase = unit.split(';')
      with open(file) as f:
        data = json.load(f)
      ret = client.get(database).bulk_docs(data)
      if len(ret) != len(data):
        print(util.bcolors.FAIL + 'might not write all data' + util.bcolors.ENDC)
        raise Exception('might not write all data')
      
      check = list(filter(lambda x: x['ok'] is not True, ret))
      if len(check) != 0:
        print(util.bcolors.FAIL + 'failed to write some data' + util.bcolors.ENDC)
        raise Exception('failed to write some data')

      print(util.bcolors.OKBLUE + 'write all data' + util.bcolors.ENDC)

    # closing
    client.disconnect()

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
