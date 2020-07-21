# Scripts to Deliver Our Solution and Dataset

## Prerequisites

Please install `pipenv`, `node`, and `npm`.

## How to Deploy

Before deploying this application, please create your IBM Cloud resource group environment. Then, please clone our solution that consists of multiple repos in [GitHub covsafe](http://example.com).

Here, we are under the assumption that you clone all repos within `/path/to/covsafe_group`.

```sh
cd /path/to/covsafe_group
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

After coffee break and the above command is finished, please deploy some services by following the next.

```sh
# deploy view
cd /path/to/covsafe_group

# deploy getters
```



access to the URL shown in the bottom of the script output with login credentials: username: "user@fake.email" and password "password".

## How to Create Dummy Data

After deployment, if you would like to get sample data generated from imaginal sensors, kick these commands below.

```sh
export APIKEY=YOUR_API_KEY
cd scripts
# change some variables for your env, like resource group
pipenv run python function-dummy-generator.py -o create -r jp-tok -g c4c-covid-19 -n dummy-generator -p dummy-generator -a dummy-generator -t dummy-generator-trigger -u dummy-generator-rule -c ./.credentials
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
