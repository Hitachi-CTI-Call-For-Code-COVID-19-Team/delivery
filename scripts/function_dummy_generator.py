#!/usr/bin/env python3

import argparse
import subprocess
import os
import sys
import json
import util

ASSETS_DB = 'assets'
ES_TOPIC = 'covsafe'

def parse_args(args):
  parser = argparse.ArgumentParser(description="""
  deploy dummy generator onto IBM Cloud Functions.
  This requires an environment variable ${APIKEY} as your IAM API key.
  """)
  parser.add_argument('-o', '--operation', default='create', help='create|delete a dummy-generator')
  parser.add_argument('-r', '--region', default='jp-tok', help='region name')
  parser.add_argument('-g', '--resource-group', default='c4c-covid-19', help='resource Group Name')
  parser.add_argument('-n', '--namespace', default='dummy-generator', help='namespace name for generator')
  parser.add_argument('-p', '--package', default='dummy-generator', help='package name for generator')
  parser.add_argument('-a', '--action', default='dummy-generator', help='action name for generator')
  parser.add_argument('-t', '--trigger', default='dummy-generator-trigger',
    help='trigger name for generator')
  parser.add_argument('-u', '--rule', default='dummy-generator-rule',
    help='rule name for generator')
  parser.add_argument(
    '-c', '--credentials-file', default='./credentials', help='file to store service credentials'
  )

  return parser.parse_args(args)


def create(args):
  args = parse_args(args)

  util.login(args.region, args.resource_group)

  util.create_functions_namespace(args.namespace)

  util.create_functions_package(args.package)

  # create config.json for dummy-generator
  # currently, the kafka javascript lib 'kafka-node' might not support cluster Kafka
  # since I got NotLeaderForPartition error.
  # it might cause sending data to the leader is executed before refreshing metadata of
  # the leader broker when the client connects to other brokers first.
  # so, this is workaround to restrict the kafkahosts to the only leader.
  # in addtion to that, kafka-node is only acceptable lib for IBM Cloud Functions
  # because the kafka-rdnode is just a wrapper of C binary, which cannot be uploaded
  # to the Cloud Functions.

  # get leader
  topic = util.get_topic_detail(ES_TOPIC)
  leader = int(topic['partition_summaries'][0]['leader'])
  # get event streams credentials and update sasl list with only leader
  es_credentials = util.get_credentials_value(
    args.credentials_file, 'EVENT_STREAMS_WRITER_CREDENTIALS'
  )
  es_credentials = json.loads(es_credentials)
  es_credentials['kafka_brokers_sasl'] = list(
    filter(
      lambda x: x.startswith('broker-{}'.format(leader)), es_credentials['kafka_brokers_sasl']
    )
  )
  # create config.json
  util.copy_credentials_to_each(
    args.credentials_file, '../functions/dummy-generator/config.json', [
      ('CLOUDANT_READER_CREDENTIALS', 'cloudant-credentials')
    ], {
      'cloudant-assets-db': ASSETS_DB,
      'es-topic': ES_TOPIC,
      'es-credentials': json.dumps(es_credentials)
    }
  )

  # build and deploy function
  print(util.bcolors.OKGREEN + 'Starting to build and deploy function' + util.bcolors.ENDC)
  p1 = subprocess.Popen([
    'sh', '../functions/dummy-generator/make.sh', args.package, args.action
  ], stdout=subprocess.PIPE)
  print(p1.communicate()[0].decode('utf-8'))
  p1 = subprocess.Popen([
    'rm', '-f', '../functions/dummy-generator/config.json'
  ], stdout=subprocess.PIPE)
  print(p1.communicate()[0].decode('utf-8'))

  # create trigger
  # you are able to see its activation by polling the log by `ibmcloud fn activation poll`
  util.create_functions_periodical_trigger(args.trigger, '"*/5 * * * *"')
  util.create_functions_rule(args.rule, args.trigger, args.package, args.action)


def delete(args):
  args = parse_args(args)

  util.login(args.region, args.resource_group)
  util.delete_functions_rule(args.rule)
  util.delete_functions_trigger(args.trigger)
  util.delete_functions_action(args.package, args.action)
  util.delete_functions_package(args.package)
  util.delete_functions_namespace(args.namespace)


if __name__ == '__main__':
  args = parse_args(sys.argv[1:])
  if args.operation == 'create':
    create(sys.argv[1:])
  elif args.operation == 'delete':
    delete(sys.argv[1:])
  else:
    print(util.bcolors.WARNING + 'no option. please check usage of this script.' + util.bcolors.ENDC)
