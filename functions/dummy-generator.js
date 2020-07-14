// IBM Cloud Functions: main function
// generate dummy sensor data
module.exports = function main(args) {
  return new Promise(function (resolve, _) {
    // get assets
    // FIXME: get from asset data collections
    const assets = [{
      deviceType: 'Congestion-Sensor',
      deviceId: 'Congestion-Sensor_1',
      eventType: 'event_1',
      sensorId: 'TOF0001',
    }, {
      deviceType: 'Congestion-Sensor',
      deviceId: 'Congestion-Sensor_2',
      eventType: 'event_2',
      sensorId: 'TOF0002',
    }];

    // this function will be kicked by a periodic trigger at each 1 min.
    // generate data within 1 min by each 10 sec.
    const timers = [];
    const data = [];
    let counter = 0;
    assets.forEach(e => {
      timers.push(setInterval(() => {
        if (++counter > assets.length * 5) {
          timers.forEach(e => clearInterval(e));
          return resolve(data);
        }
        data.push(generate(e.deviceType, e.deviceId, e.eventType, new Date(), e.sensorId));
      }, 10000));
    });
  });
}

function generate(deviceType, deviceId, eventType, timestamp, sensorId) {
  const data = {
    deviceType: deviceType,
    deviceId: deviceId,
    eventType: eventType,
    format: 'json',
    timestamp: timestamp
  };
  switch (deviceType) {
    case 'Congestion-Sensor': data.data = generateCongestion(timestamp, sensorId); break;
  }
  return data;
}

function generateCongestion(timestamp, sensorId) {
  const MAX = 50;
  return {
    "Timestamp": timestamp,
    "SensorId": sensorId,
    "NumberOfPersons": Math.floor(Math.random() * MAX)
  };
}