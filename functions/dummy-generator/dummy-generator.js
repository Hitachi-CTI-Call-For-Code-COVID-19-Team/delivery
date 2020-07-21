const Cloudant = require('@cloudant/cloudant');
const kafka = require('kafka-node');
const { fill } = require('lodash');

const PERIOD = 30000;
const PERIODIC_TRIGGER_PERIOD = 60000;
const LOOP = Math.floor(PERIODIC_TRIGGER_PERIOD / PERIOD - 1);

// IBM Cloud Functions: main function
// generate dummy sensor data
function main(params) {
  return new Promise(function (resolve, reject) {
    // get assets
    getdata(params)
      .then(res => {
        const assets = res;
        const assets_len = assets.filter(
          e => !['site', 'building', 'outside', 'floor'].some(t => t === e.doc.type)
        ).length;

        // this function will be kicked by a periodic trigger at each 1 min.
        // generate data within 1 min by each PERIOD sec.
        function generateAndPush(assets) {
          return new Promise(function (resolve, reject) {
            const data = [];
            assets.forEach((e, i) => {
              if (['site', 'building', 'outside', 'floor'].some(t => t === e.doc.type)) {
                // no need to create events
                return;
              }
              // the same timespamp of all data might cause an error when getting data from es
              let date = new Date(new Date().getTime() + i)
              data.push(generate(e.doc.id, e.doc.type, e.doc.subType, date, e.doc.settings));
            });

            if (!data.length) {
              return resolve({ message: 'there is no assets' });
            }
            return pushdata(params, data)
              .then(res => resolve(res))
              .catch(err => reject(err));
          });
        }

        // fist one done immediately
        generateAndPush(assets)
          .then(res => console.log(`done the first genrating and pushing: ${res}`))
          .catch(err => console.error(`got error while first generating: ${err}`));

        // next ones
        const timers = [];
        let counter = 0;
        timers.push(setInterval(() => {
          if (++counter >= LOOP) {
            timers.forEach(e => clearInterval(e));
          }
          generateAndPush(assets)
            .then(res => counter >= LOOP ? resolve(res) : console.log(`${counter}: done`))
            .catch(err => counter >= LOOP ? reject(err) : console.error(`${counter}: error`));
        }, PERIOD));
      })
      .catch(err => reject({ error: err.toString() }));
  });
}

// when used as zip
// module.exports = main;
// when used as js
global.main = main;

/*
  get assets data from cloudant DB. params should have those properties.
  @cloudant-credentials {string} is as json string including reader credentials for cloudant
  @cloudant-assets-db {string} is database name to get assets data
*/
function getdata(params) {
  return new Promise(function (resolve, reject) {
    // getting parameters
    const url = _getURL(JSON.parse(params['cloudant-credentials']));
    if (url instanceof Error) {
      return reject(url);
    }
    if (!params['cloudant-assets-db']) {
      return reject(new Error('invalid param. it should have db name as db'));
    }

    // create db and read all data
    const db = Cloudant(url).use(params['cloudant-assets-db']);
    db.list({ include_docs: true })
      .then(res => {
        resolve(res.rows);
      })
      .catch(e => reject(e));
  });
}

function putdata(params, database, data) {
  return new Promise(function (resolve, reject) {
    // getting parameters
    const url = _getURL(JSON.parse(params['cloudant-credentials']));
    if (url instanceof Error) {
      return reject(url);
    }
    if (!database && !params['cloudant-assets-db']) {
      return reject(new Error('invalid param. it should have db name as db'));
    }

    // create db and write all data
    const db = Cloudant(url).use(database || params['cloudant-assets-db']);
    db.bulk({ docs: data })
      .then(res => {
        if (res.length !== data.length) {
          return reject(new Error('might not write some data'));
        }
        if (res.map(e => e.ok).filter(e => !e).length !== 0) {
          return reject(new Error('might not fail to write some data'));
        }
        resolve(res);
      })
      .catch(e => reject(e));
  });
}

function _getURL(params) {
  let url;
  if (!params.url) {
    return new Error('invalid param. it should have url');
  } else if (params.url.match(/https*:\/\/.*:.*@.*\.cloudantnosqldb.appdomain.cloud/)) {
    url = params.url;
  } else if (params.username && params.password) {
    isHTTP = params.url.indexOf('http://') === 0;
    host = params.url.slice(isHTTP ? 7 : 8);
    url = `${isHTTP ? 'http' : 'https'}://${params.username}:${params.password}@${host}`;
    url = params.port ? (url + ':' + params.port) : url;
  }
  return url;
}

function generate(id, type, subType, timestamp, options) {
  const data = {
    deviceType: generateDeviceType(type, subType),
    deviceId: generateDeviceId(id, type, subType),
    eventType: 'send_data',
  };
  switch (type) {
    case 'area':
    case 'line': data.data = generateCongestion(id, timestamp, options); break;
    case 'thing':
      switch (subType) {
        case 'garbage_bin': data.data = generateDisinfection(id, timestamp); break;
        case 'handwash_stand': data.data = generateSanitization(id, timestamp); break;
      }
      break;
  }
  return data;
}

function generateDeviceType(type, subType) {
  switch(type) {
    case 'area': return 'area_people_counter';
    case 'line': return 'line_people_counter';
    case 'thing':
      switch (subType) {
        case 'garbage_bin': return 'garbage_bin_monitor';
        case 'handwash_stand': return 'handwash_monitor';
      }
  }
  return undefined;
}

function generateDeviceId(id, type, subType) {
  switch (type) {
    case 'area': return `area_people_counter-${id}`;
    case 'line': return `line_people_counter-${id}`;
    case 'thing':
      switch (subType) {
        case 'garbage_bin': return `garbage_bin_monitor-${id}`;
        case 'handwash_stand': return `handwash_monitor-${id}`;
      }
  }
  return undefined;
}

function generateCongestion(id, timestamp, options) {
  const MAX = 50;
  const COEF = options && options.coef ? 1 + options.coef : 1;
  return {
    payload: {
      area: `${id}`,
      count: Math.floor(Math.min(0.99, Math.random() * COEF) * MAX),
      period: PERIOD,
    },
    time: timestamp
  };
}

function generateSanitization(id, timestamp) {
  const MAX_DEPTH = 100;
  const filled = Math.floor(Math.random() * MAX_DEPTH);
  return {
    payload: {
      garbageBin: `${id}`,
      distance: filled,
      max_depth: MAX_DEPTH,
      amount_rate: Math.floor(((MAX_DEPTH - filled) / MAX_DEPTH) * 100),
    },
    time: timestamp,
  };
}

function generateDisinfection(id, timestamp) {
  const MAX = 10;
  return {
    payload: {
      handwashStand: `${id}`,
      count: Math.floor(Math.random() * MAX),
      period: PERIOD,
    },
    time: timestamp,
  };
}

function pushdata(params, data) {
  return new Promise(function (resolve, reject) {
    const credentials = JSON.parse(params['es-credentials']);

    // create kafka connection
    const client = new kafka.KafkaClient({
      kafkaHost: credentials.kafka_brokers_sasl.join(','),
      sslOptions: {
        rejectUnauthorized: false,
        servername: credentials.kafka_brokers_sasl[0].match(/(.*):.*/)[1],
      },
      sasl: {
        mechanism: 'plain',
        username: credentials.user,
        password: credentials.api_key,
      }
    });

    // create a producer
    const producer = new kafka.HighLevelProducer(client);
    const payloads = data.map(d => ({
      topic: params['es-topic'],
      messages: JSON.stringify(d),
    }));

    producer.on('ready', () => {
      console.log('on tap to push data to streams');

      // send messages
      // producer.send(payloads, (err, data) => {
      //   if (err) {
      //     console.error(`got error by send(): ${err}`);
      //     return reject(new Error(`got error by send(): ${err}`));
      //   }
      //   resolve({ message: `all data was sent: ${data}` });
      // });
      // currently, data recorder only support one by one sending
      let counter = 0;
      const errors = [];
      payloads.forEach((payload, i) => {
        producer.send([payload], (err, data) => {
          counter++;
          if (err) {
            console.error(`got error by send(): ${err}`);
            errors.push(`${i}: ${err}`);
          }
          if (counter >= payloads.length) {
            if (errors.length) {
              reject(new Error(errors));
            } else {
              resolve({ message: 'all data was sent' });
            }
          }
        });
      });
    });
    producer.on('error', (err) => {
      console.error(`got error before sending message: ${err}`);
      reject(new Error(`got error before sending message: ${err.toString()}`));
    });
    producer.on('brokersChanged', (err) => {
      // basically this shouldn't occur, but it happens when sending messages into one partition
      // from multiple clients
      console.error(`got brokers changed event: ${err}`);
      reject(new Error(`got brokers changed event: ${err}`));
    });
  });
}