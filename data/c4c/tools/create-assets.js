/*
Copyright 2020 Hitachi Ltd.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

  http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
*/

// usage:
// node ./create-assets.js TENANT_NAME
// TENANT_NAME: should be the dir name under /data

const _ = require('lodash');
const fs = require('fs');
const path = require('path');

// cell size of coordinate on your map
const HEIGHT = 67.5;
const WIDTH = 60;

const SUPERASSETS = [
  {
    id: 'imaginary-shopping-mall',
    name: `dreamy-shopping-mall`,
    description: 'shopping mall that involve you in the deam world',
    type: 'site',
    subType: undefined,
    belongs: undefined,
    belongings: ['imaginary-shopping-mall-building', 'imaginary-shopping-mall-outside'],
    mapCoordinate: {
      lat: 0,
      lng: 0,
      height: 1080,
      width: 1920
    },
    // currently, we don't use them
    realCoordinate: {},
    settings: {},
  }, {
    id: 'imaginary-shopping-mall-building',
    name: `dreamy-shopping-mall-building`,
    description: 'shopping mall that involve you in the deam world',
    type: 'building',
    subType: undefined,
    belongs: 'imaginary-shopping-mall',
    belongings: ['imaginary-shopping-mall-1st-floor'],
    mapCoordinate: {
      lat: 0,
      lng: 0,
      height: 1080,
      width: 1920
    },
    // currently, we don't use them
    realCoordinate: {},
    settings: {},
  }, {
    id: 'imaginary-shopping-mall-outside',
    name: `dreamy-shopping-mall-outside`,
    description: 'shopping mall that involve you in the deam world',
    type: 'outside',
    subType: undefined,
    belongs: 'imaginary-shopping-mall',
    belongings: [],
    mapCoordinate: {
      lat: 0,
      lng: 0,
      height: 1080,
      width: 1920
    },
    // currently, we don't use them
    realCoordinate: {},
    settings: {},
  }, {
    id: 'imaginary-shopping-mall-1st-floor',
    name: `dreamy-shopping-mall-1st-floor`,
    description: '1st floor of the imaginary shopping mall',
    type: 'floor',
    subType: undefined,
    belongs: 'imaginary-shopping-mall-building',
    belongings: [],
    mapCoordinate: {
      lat: 0,
      lng: 0,
      height: 1080,
      width: 1920
    },
    // currently, we don't use them
    realCoordinate: {},
    settings: {},
  }
];

var logicals = SUPERASSETS.concat(_.range(0, 1920, 60).reduce((p1, lng) => {
  p1 = p1.concat(_.range(0, 1080, 67.5).reduce((p2, lat) => {
    p2 = p2.concat((() => {
      const assets = [];
      // congestion
      assets.push({
        id: `congestion-${lat}-${lng}`,
        name: `congestion-${lat}-${lng}`,
        description: 'logical congestion area',
        type: 'area',
        subType: (() => {
          if (lng < 840 && lat >= 945) return 'parking';
          else if (lng < 960 && lat >= 945) return 'roadway';
          else if (lng < 960 && lat >= 877.5) return 'roadway';
          else if (lng >= 840 && lat >= 742.5 && lng < 960 && lat < 877.5) return 'roadway';
          else if (lng >= 960 && lat >= 810 && lng < 1620) return 'parking';
          else if (lng >= 1620 && lat >= 810 && lng < 1680 && lat < 1012.5) return 'parking';
          else if (lng >= 1680 && lat >= 810 && lng < 1740 && lat < 877.5) return 'parking';
          else if (lng >= 1680 && lat >= 877.5 && lng < 1740 && lat < 945) return 'parking';
          else if (lng >= 960 && lat >= 742.5 && lng < 1740 && lat < 810) return 'roadway';
          else if (lng >= 0 && lat >= 0 && lng < 420 && lat < 202.5) return 'parking';
          else if (lng >= 0 && lat >= 202.5 && lng < 480 && lat < 270) return 'roadway';
          else if (lng >= 420 && lat >= 135 && lng < 480 && lat < 202.5) return 'roadway';
          else if (lng >= 420 && lat >= 0 && lng < 1260 && lat < 135) return 'roadway';
          else if (lng >= 1260 && lat >= 67.5 && lng < 1800 && lat < 135) return 'roadway';
          else if (lng >= 1620 && lat >= 135 && lng < 1920 && lat < 270) return 'roadway';
          else if (lng >= 1740 && lat >= 135 && lng < 1740 && lat < 202.5) return 'roadway';
          else if (lng >= 1740 && lat >= 742.5 && lng < 1800 && lat < 877.5) return 'roadway';
          else if (lng >= 0 && lat >= 270 && lng < 120 && lat < 405) return 'toilet';
          else if (lng >= 120 && lat >= 270 && lng < 540 && lat < 405) return 'aisle';
          else if (lng >= 0 && lat >= 405 && lng < 300 && lat < 877.5) return 'shop';
          else if (lng >= 300 && lat >= 405 && lng < 360 && lat < 877.5) return 'aisle';
          else if (lng >= 360 && lat >= 405 && lng < 840 && lat < 607.5) return 'shop';
          else if (lng >= 360 && lat >= 607.5 && lng < 840 && lat < 675) return 'aisle';
          else if (lng >= 360 && lat >= 675 && lng < 840 && lat < 877.5) return 'shop';
          else if (lng >= 480 && lat >= 135 && lng < 540 && lat < 270) return 'aisle';
          else if (lng >= 540 && lat >= 135 && lng < 960 && lat < 337.5) return 'shop';
          else if (lng >= 540 && lat >= 337.5 && lng < 840 && lat < 405) return 'aisle';
          else if (lng >= 840 && lat >= 337.5 && lng < 1020 && lat < 742.5) return 'aisle';
          else if (lng >= 960 && lat >= 135 && lng < 1020 && lat < 405) return 'aisle';
          else if (lng >= 1020 && lat >= 135 && lng < 1260 && lat < 337.5) return 'shop';
          else if (lng >= 1260 && lat >= 135 && lng < 1320 && lat < 337.5) return 'aisle';
          else if (lng >= 1320 && lat >= 135 && lng < 1500 && lat < 337.5) return 'shop';
          else if (lng >= 1500 && lat >= 270 && lng < 1560 && lat < 337.5) return 'shop';
          else if (lng >= 1500 && lat >= 135 && lng < 1560 && lat < 270) return 'toilet';
          else if (lng >= 1560 && lat >= 135 && lng < 1620 && lat < 405) return 'aisle';
          else if (lng >= 1020 && lat >= 337.5 && lng < 1560 && lat < 607.5) return 'aisle';
          else if (lng >= 1020 && lat >= 607.5 && lng < 1560 && lat < 742.5) return 'shop';
          else if (lng >= 1560 && lat >= 405 && lng < 1620 && lat < 742.5) return 'shop';
          else if (lng >= 1620 && lat >= 202.5 && lng < 1800 && lat < 742.5) return 'shop';
          else if (lng >= 1800 && lat >= 270 && lng < 1860 && lat < 607.5) return 'shop';
          else if (lng >= 1860 && lat >= 270 && lng < 1920 && lat < 405.5) return 'shop';
          else return 'unknown';
        })(),
        belongs: (() => {
          if (lng < 840 && lat >= 945) return 'imaginary-shopping-mall-outside';
          else if (lng < 960 && lat >= 945) return 'imaginary-shopping-mall-outside';
          else if (lng < 960 && lat >= 877.5) return 'imaginary-shopping-mall-outside';
          else if (lng >= 840 && lat >= 742.5 && lng < 960 && lat < 877.5) return 'imaginary-shopping-mall-outside';
          else if (lng >= 960 && lat >= 810 && lng < 1620) return 'imaginary-shopping-mall-outside';
          else if (lng >= 1620 && lat >= 810 && lng < 1680 && lat < 1012.5) return 'imaginary-shopping-mall-outside';
          else if (lng >= 960 && lat >= 742.5 && lng < 1740 && lat < 810) return 'imaginary-shopping-mall-outside';
          else if (lng >= 0 && lat >= 0 && lng < 420 && lat < 202.5) return 'imaginary-shopping-mall-outside';
          else if (lng >= 0 && lat >= 202.5 && lng < 480 && lat < 270) return 'imaginary-shopping-mall-outside';
          else if (lng >= 420 && lat >= 0 && lng < 1260 && lat < 135) return 'imaginary-shopping-mall-outside';
          else if (lng >= 1260 && lat >= 67.5 && lng < 1800 && lat < 135) return 'imaginary-shopping-mall-outside';
          else if (lng >= 1620 && lat >= 135 && lng < 1920 && lat < 270) return 'imaginary-shopping-mall-outside';
          else if (lng >= 1740 && lat >= 135 && lng < 1740 && lat < 202.5) return 'imaginary-shopping-mall-outside';
          else if (lng >= 0 && lat >= 270 && lng < 120 && lat < 405) return 'imaginary-shopping-mall-1st-floor';
          else if (lng >= 120 && lat >= 270 && lng < 540 && lat < 405) return 'imaginary-shopping-mall-1st-floor';
          else if (lng >= 0 && lat >= 405 && lng < 300 && lat < 877.5) return 'imaginary-shopping-mall-1st-floor';
          else if (lng >= 300 && lat >= 405 && lng < 360 && lat < 877.5) return 'imaginary-shopping-mall-1st-floor';
          else if (lng >= 360 && lat >= 405 && lng < 840 && lat < 607.5) return 'imaginary-shopping-mall-1st-floor';
          else if (lng >= 360 && lat >= 607.5 && lng < 840 && lat < 675) return 'imaginary-shopping-mall-1st-floor';
          else if (lng >= 360 && lat >= 675 && lng < 840 && lat < 877.5) return 'imaginary-shopping-mall-1st-floor';
          else if (lng >= 480 && lat >= 135 && lng < 540 && lat < 270) return 'imaginary-shopping-mall-1st-floor';
          else if (lng >= 540 && lat >= 135 && lng < 960 && lat < 337.5) return 'imaginary-shopping-mall-1st-floor';
          else if (lng >= 540 && lat >= 337.5 && lng < 840 && lat < 405) return 'imaginary-shopping-mall-1st-floor';
          else if (lng >= 840 && lat >= 337.5 && lng < 1020 && lat < 742.5) return 'imaginary-shopping-mall-1st-floor';
          else if (lng >= 960 && lat >= 135 && lng < 1020 && lat < 405) return 'imaginary-shopping-mall-1st-floor';
          else if (lng >= 1020 && lat >= 135 && lng < 1260 && lat < 337.5) return 'imaginary-shopping-mall-1st-floor';
          else if (lng >= 1260 && lat >= 135 && lng < 1320 && lat < 337.5) return 'imaginary-shopping-mall-1st-floor';
          else if (lng >= 1320 && lat >= 135 && lng < 1500 && lat < 337.5) return 'imaginary-shopping-mall-1st-floor';
          else if (lng >= 1500 && lat >= 270 && lng < 1560 && lat < 337.5) return 'imaginary-shopping-mall-1st-floor';
          else if (lng >= 1500 && lat >= 135 && lng < 1560 && lat < 270) return 'imaginary-shopping-mall-1st-floor';
          else if (lng >= 1560 && lat >= 135 && lng < 1620 && lat < 405) return 'imaginary-shopping-mall-1st-floor';
          else if (lng >= 1020 && lat >= 337.5 && lng < 1560 && lat < 607.5) return 'imaginary-shopping-mall-1st-floor';
          else if (lng >= 1020 && lat >= 607.5 && lng < 1560 && lat < 742.5) return 'imaginary-shopping-mall-1st-floor';
          else if (lng >= 1560 && lat >= 405 && lng < 1620 && lat < 742.5) return 'imaginary-shopping-mall-1st-floor';
          else if (lng >= 1620 && lat >= 202.5 && lng < 1800 && lat < 742.5) return 'imaginary-shopping-mall-1st-floor';
          else if (lng >= 1800 && lat >= 270 && lng < 1860 && lat < 607.5) return 'imaginary-shopping-mall-1st-floor';
          else if (lng >= 1860 && lat >= 270 && lng < 1920 && lat < 405.5) return 'imaginary-shopping-mall-1st-floor';
          else return 'unknown';
        })(),
        belongings: [],
        mapCoordinate: {
          lat: lat,
          lng: lng,
          height: HEIGHT,
          width: WIDTH
        },
        // currently, we don't use them
        realCoordinate: {},
        settings: {
          coef: (() => {
            if (lng >= 1740 && lat < 742.5) return 0.0;
            else if (lng >= 1800 && lat >= 540) return 0.0;
            else if (lng < 60 || lng >= 1860) return 0.0;
            else if (lat < 135 || lat >= 877.5) return 0.3;
            else if (lng < 480 && lat < 337.5) return 0.3;
            else if (lng >= 1620 && lat < 270) return 0.3;
            else if (lng >= 960 && lat >= 742.5) return 0.3;
            else if (lng >= 1740 && lat >= 337.5) return 0.3;
            else if (lng >= 1020 && lat >= 337.5 && lng < 1500 && lat < 607.5) return 0.9;
            else if (lng >= 240 && lat >= 540 && lng < 600 && lat < 742.5) return 0.9;
            else return 0.6;
          })(),
        },
      });

      // garbage bin
      if (
        (lng >= 120 && lat >= 270 && lng < 180 && lat < 337.5) ||
        (lng >= 300 && lat >= 810 && lng < 360 && lat < 877.5) ||
        (lng >= 480 && lat >= 135 && lng < 540 && lat < 202.5) ||
        (lng >= 780 && lat >= 270 && lng < 840 && lat < 337.5) ||
        (lng >= 1260 && lat >= 135 && lng < 1320 && lat < 202.5) ||
        (lng >= 1560 && lat >= 135 && lng < 1620 && lat < 202.5) ||
        (lng >= 1380 && lat >= 405 && lng < 1440 && lat < 472.5) ||
        (lng >= 1560 && lat >= 540 && lng < 1620 && lat < 607.5) ||
        (lng >= 1800 && lat >= 405 && lng < 1860 && lat < 472.5)
      ) {
        assets[0].belongings.push(`disinfection-${lat}-${lng}`);

        assets.push({
          id: `disinfection-${lat}-${lng}`,
          name: `disinfection-${lat}-${lng}`,
          description: 'garbage bin monitoring for disinfection',
          type: 'thing',
          subType: (() => 'garbage_bin')(),
          belongs: (() => 'imaginary-shopping-mall-1st-floor')(),
          belongings: [],
          mapCoordinate: {
            lat: lat,
            lng: lng,
            height: HEIGHT,
            width: WIDTH
          },
          // currently, we don't use them
          realCoordinate: {},
          settings: {},
        });
      }

      // handwash stand
      if (
        (lng >= 60 && lat >= 270 && lng < 120 && lat < 405) ||
        (lng >= 1500 && lat >= 135 && lng < 1560 && lat < 270)
      ) {
        assets[0].belongings.push(`sanitization-${lat}-${lng}`);

        assets.push({
          id: `sanitization-${lat}-${lng}`,
          name: `sanitization-${lat}-${lng}`,
          description: 'hand washing monitoring for sanitization',
          type: 'thing',
          subType: (() => 'handwash_stand')(),
          belongs: (() => 'imaginary-shopping-mall-1st-floor')(),
          belongings: [],
          mapCoordinate: {
            lat: lat,
            lng: lng,
            height: HEIGHT,
            width: WIDTH
          },
          // currently, we don't use them
          realCoordinate: {},
          settings: {},
        });
      }

      return assets;
    })());
    return p2;
  }, []));
  return p1;
}, []));

// delete area outside of mall
logicals = logicals.filter(e => e.subType !== 'unknown');
// add belongings
var outside = logicals.find(e => e.id === 'imaginary-shopping-mall-outside');
var floor = logicals.find(e => e.id === 'imaginary-shopping-mall-1st-floor');
outside.belongings = logicals
  .filter(e => (e.subType === 'parking' || e.subType === 'roadway' || e.subType === 'walkway'))
  .map(e => e.id);
floor.belongings = logicals
  .filter(e => (e.subType === 'toilet' || e.subType === 'aisle' || e.subType === 'shop'))
  .map(e => e.id);

// workers
const workers = _.range(50).map(_ => ({
  // to be updated
}));

function createAssets() {
  let assets = [];

  // add logical assets
  assets = assets.concat(logicals.map(l => ({ ...l, isLogical: true })));

  // there are no phisical assets for this case

  // write to file
  fs.writeFile(path.join(__dirname, '..', 'assets.json'), JSON.stringify(assets), (err) => {
    if (err) throw err;
  });

  return assets;
}

// main
if (require.main === module) {
  createAssets();
} else {
  module.exports = createAssets;
}