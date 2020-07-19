#!/bin/sh

set -eu

PACKAGE_NAME=$1
ACTION_NAME=$2

SCRIPT_DIR=$(cd $(dirname $0); pwd)
WORK_DIR=${SCRIPT_DIR}
export PACKAGE=${PACKAGE_NAME}
export ACTION=${ACTION_NAME}

pushd .
cd ${WORK_DIR}
if [ ! -e "${WORK_DIR}/config.json" ]; then
  echo "need config.json that includes cloudant url, username and password"
  exit 1
fi

npm install
npm run build
npm run deploy:ibm

rm -rf node_modules
rm -f package-lock.json *.bundle.js
unset PACKAGE, ACTION

popd
