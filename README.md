# Scripts to Deliver Our Solution and Dataset

## Prerequisites

Before deploying this application, please create your IBM Cloud resource group environment. Then, please clone our solution that consists of multiple repos in [Hitachi CTI Call For Code COVID-19 Team](https://github.com/Hitachi-CTI-Call-For-Code-COVID-19-Team). Here, we are under the assumption that you clone all repos within `/path/to/COVSAFE`.

In addition to above, please install `python`, `pipenv`, `node`, and `npm`. Those are required for building and deploying our application.

## Preparation

Before building and deploying our application, you should create some configurations and assets.

### Create assets




## How to deploy


1. Create IBM Cloud Functions Namespace

The Covsafe solution uses some Functions namespaces which should define prior to deployment of some services.

```sh
cd delivery
cd scripts
pipenv install
pipenv run python namespaces.py -o create -r jp-tok -g c4c-civid-19
```

2. Create Servcies

```sh
cd delivery

# if you want sample assets data to be set, please these two commands below.
cd ./delivery/data/c4c/tools
npm install
npm start

# dploy covsafe solution
export APIKEY=YOUR_API_KEY
cd scripts
pipenv install
# change some variables for your env, like resource group
pipenv run python main.py -o create -p covsafe -t c4c -r jp-tok -g c4c-civid-19
```

3. Deploy Functions

See README of each repo to get known how to buid and deploy the frontend function. The covsafe solution has functions listed below.

- solution-management-console
- getters/reader
- risk-calculator
- risk-notifier
- data-recorder

4. Check it

After coffee break and the above command is finished, please deploy some services by following the next.
access to the URL shown in the bottom of the script output with login credentials: username: "user@fake.email" and password "password".

## How to Create Dummy Data

After deployment, if you would like to get sample data generated from imaginal sensors, kick these commands below.

```sh
export APIKEY=YOUR_API_KEY
cd scripts
# change some variables for your env, like resource group
pipenv run python function_dummy_generator.py -o create -r jp-tok -g c4c-covid-19 -n dummy-generator -p dummy-generator -a dummy-generator -t dummy-generator-trigger -u dummy-generator-rule -c ./.credentials
```

## How to Delete the Solution

```sh
# dploy covsafe solution
export APIKEY=YOUR_API_KEY
cd scripts
pipenv install
# change some variables for your env, like resource group
pipenv run python main.py -o delete -p covsafe -t c4c -r jp-tok -g c4c-civid-19
```



Order

- create configuration
  - asset: configuration

- create ui ns

- create instances
- create service keys
- create database
  - assets, assets_staff, view-config, log_risk_calculation, log_risk_notifier, a_notification_template, ads, shops
- push initial data
  - floormap.png
  - assets.json
  - view-config.json
- need to create index to avoid the query error

- app id secret info <- ui redirect URL

db bucket

- functions
  - data-proxy api <- deploy before ui
  - risk calculation/notifier

- ui

