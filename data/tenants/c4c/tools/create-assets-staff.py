#
# Copyright 2020 Hitachi Ltd.
 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
 
#  http://www.apache.org/licenses/LICENSE-2.0
 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

#
#
# main() will be run when you invoke this action
#
# @param Cloud Functions actions accept a single parameter, which must be a JSON object.
#
# @return The output of this action, which must be a JSON object.
#

# GOAL: To generate dummy dat to simulate store-staffs' and their devices' parameters

import random
import json

def main(dict):

    data = {
        "staff": {
            "id": ["st0001", "st0002", "st0003", "st0004", "st0005", "st0006", "st0007", "st0008", "st0009", "st0010", "st0011", "st0012", "st0013", "st0014", "st0015", "st0016", "st0017"],
            "deviceId": ["D8AA1D5F-A10E-4C09-98BA-BD481709E11D", "D8AA1D5F-A10E-4C09-98BA-BD481709E12D", "D8AA1D5F-A10E-4C09-98BA-BD481709E13D", "D8AA1D5F-A10E-4C09-98BA-BD481709E14D", "D8AA1D5F-A10E-4C09-98BA-BD481709E15D", "D8AA1D5F-A10E-4C09-98BA-BD481709E16D", "D8AA1D5F-A10E-4C09-98BA-BD481709E17D", "D8AA1D5F-A10E-4C09-98BA-BD481709E18D", "D8AA1D5F-A10E-4C09-98BA-BD481709E19D", "D8AA1D5F-A10E-4C09-98BA-BD481709E20D", "D8AA1D5F-A10E-4C09-98BA-BD481709E21D", "D8AA1D5F-A10E-4C09-98BA-BD481709E22D", "D8AA1D5F-A10E-4C09-98BA-BD481709E23D", "D8AA1D5F-A10E-4C09-98BA-BD481709E24D", "D8AA1D5F-A10E-4C09-98BA-BD481709E25D", "D8AA1D5F-A10E-4C09-98BA-BD481709E26D", "D8AA1D5F-A10E-4C09-98BA-BD481709E27D"],
            "roles": ["counter", "aisle-arrangement", "store-cleaning", "ware-house", "toilet-cleaning"],
            "time_slot": {
                "slot01": {"start": "9:00:00", "end": "11:00:00"},
                "slot02": {"start": "10:00:00", "end": "12:00:00"},
                "slot03": {"start": "11:00:00", "end": "13:00:00"},
                "slot04": {"start": "12:00:00", "end": "14:00:00"},
                "slot05": {"start": "13:00:00", "end": "15:00:00"},
                "slot06": {"start": "14:00:00", "end": "16:00:00"},
                "slot07": {"start": "15:00:00", "end": "17:00:00"},
                "slot08": {"start": "16:00:00", "end": "18:00:00"},
                "slot09": {"start": "17:00:00", "end": "19:00:00"},
                "slot10": {"start": "18:00:00", "end": "20:00:00"},
                "slot11": {"start": "19:00:00", "end": "21:00:00"},
                "slot12": {"start": "20:00:00", "end": "22:00:00"}
            },
            "belongs": ["congestion-0-0", "congestion-67.5-0", "congestion-135-0", "congestion-202.5-0", "congestion-877.5-0", "congestion-945-0", "congestion-1012.5-0", "congestion-0-60", "congestion-67.5-60", "congestion-135-60", "congestion-202.5-60", "congestion-877.5-60", "congestion-945-60", "congestion-1012.5-60", "congestion-0-120", "congestion-67.5-120", "congestion-135-120", "congestion-202.5-120", "congestion-877.5-120", "congestion-945-120", "congestion-1012.5-120", "congestion-0-180", "congestion-67.5-180", "congestion-135-180", "congestion-202.5-180", "congestion-877.5-180", "congestion-945-180", "congestion-1012.5-180", "congestion-0-240", "congestion-67.5-240", "congestion-135-240", "congestion-202.5-240", "congestion-877.5-240", "congestion-945-240", "congestion-1012.5-240", "congestion-0-300", "congestion-67.5-300", "congestion-135-300", "congestion-202.5-300", "congestion-877.5-300", "congestion-945-300", "congestion-1012.5-300", "congestion-0-360", "congestion-67.5-360", "congestion-135-360", "congestion-202.5-360", "congestion-877.5-360", "congestion-945-360", "congestion-1012.5-360", "congestion-0-420", "congestion-67.5-420", "congestion-135-420", "congestion-202.5-420", "congestion-877.5-420", "congestion-945-420", "congestion-1012.5-420", "congestion-0-480", "congestion-67.5-480", "congestion-877.5-480", "congestion-945-480", "congestion-1012.5-480", "congestion-0-540", "congestion-67.5-540", "congestion-877.5-540", "congestion-945-540", "congestion-1012.5-540", "congestion-0-600", "congestion-67.5-600", "congestion-877.5-600", "congestion-945-600", "congestion-1012.5-600", "congestion-0-660", "congestion-67.5-660", "congestion-877.5-660", "congestion-945-660", "congestion-1012.5-660", "congestion-0-720", "congestion-67.5-720", "congestion-877.5-720", "congestion-945-720", "congestion-1012.5-720", "congestion-0-780", "congestion-67.5-780", "congestion-877.5-780", "congestion-945-780", "congestion-1012.5-780", "congestion-0-840", "congestion-67.5-840", "congestion-742.5-840", "congestion-810-840", "congestion-877.5-840", "congestion-945-840", "congestion-1012.5-840", "congestion-0-900", "congestion-67.5-900", "congestion-742.5-900", "congestion-810-900", "congestion-877.5-900", "congestion-945-900", "congestion-1012.5-900", "congestion-0-960", "congestion-67.5-960", "congestion-742.5-960", "congestion-810-960", "congestion-877.5-960", "congestion-945-960", "congestion-1012.5-960", "congestion-0-1020", "congestion-67.5-1020", "congestion-742.5-1020", "congestion-810-1020", "congestion-877.5-1020", "congestion-945-1020", "congestion-1012.5-1020", "congestion-0-1080", "congestion-67.5-1080", "congestion-742.5-1080", "congestion-810-1080", "congestion-877.5-1080", "congestion-945-1080", "congestion-1012.5-1080", "congestion-0-1140", "congestion-67.5-1140", "congestion-742.5-1140", "congestion-810-1140", "congestion-877.5-1140", "congestion-945-1140", "congestion-1012.5-1140", "congestion-0-1200", "congestion-67.5-1200", "congestion-742.5-1200", "congestion-810-1200", "congestion-877.5-1200", "congestion-945-1200", "congestion-1012.5-1200", "congestion-67.5-1260", "congestion-742.5-1260", "congestion-810-1260", "congestion-877.5-1260", "congestion-945-1260", "congestion-1012.5-1260", "congestion-67.5-1320", "congestion-742.5-1320", "congestion-810-1320", "congestion-877.5-1320", "congestion-945-1320", "congestion-1012.5-1320", "congestion-67.5-1380", "congestion-742.5-1380", "congestion-810-1380", "congestion-877.5-1380", "congestion-945-1380", "congestion-1012.5-1380", "congestion-67.5-1440", "congestion-742.5-1440", "congestion-810-1440", "congestion-877.5-1440", "congestion-945-1440", "congestion-1012.5-1440", "congestion-67.5-1500", "congestion-742.5-1500", "congestion-810-1500", "congestion-877.5-1500", "congestion-945-1500", "congestion-1012.5-1500", "congestion-67.5-1560", "congestion-742.5-1560", "congestion-810-1560", "congestion-877.5-1560", "congestion-945-1560", "congestion-1012.5-1560", "congestion-67.5-1620", "congestion-135-1620", "congestion-202.5-1620", "congestion-742.5-1620", "congestion-810-1620", "congestion-877.5-1620", "congestion-945-1620", "congestion-67.5-1680", "congestion-135-1680", "congestion-202.5-1680", "congestion-742.5-1680", "congestion-810-1680", "congestion-877.5-1680", "congestion-67.5-1740", "congestion-135-1740", "congestion-202.5-1740", "congestion-742.5-1740", "congestion-810-1740", "congestion-135-1800", "congestion-202.5-1800", "congestion-135-1860", "congestion-202.5-1860"]
        },

        "manager": {
            "id": ["mg0001", "mg0002", "mg0003"],
            "deviceId": ["D8AA1D5F-A10E-4C09-98BA-BD481709E28D", "D8AA1D5F-A10E-4C09-98BA-BD481709E29D", "D8AA1D5F-A10E-4C09-98BA-BD481709E30D"],
            "roles": ["logistics", "customer-service", "orders"],
            "time_slot": {
                "slot01": {"start": "9:00:00", "end": "17:00:00"},
                "slot02": {"start": "14:00:00", "end": "22:00:00"}
            },
            "belongs": ["imaginary-shopping-mall-1st-floor", "imaginary-shopping-mall-2nd-floor"]
        }
    }

    madeData = []
    for x in range(0, 17):
        madeData.append(makeData(data["staff"], "staff", x)["returnVal"])
    for x in range(0, 3):
        madeData.append(makeData(data["manager"], "manager", x)["returnVal"])

    return {"docs": json.dumps({"docs": (madeData)}),
            "dbname": "assets_staff"
            }


def makeData(dict, typeA, x):
    # target = random.choices([list(data.keys())], weights=[80, 20], k=1)
    #     target = random.choices(["staff","manager"], weights=[90, 10], k=1)
    target = list(dict.keys())[0]
    dict0 = dict  # dict[target[0]]
    sampleStaffData = {
        "type": typeA,
        # "_id": dict0["id"][x],
        "id": dict0["id"][x],
        # dict0["deviceId"][x],
        "deviceId":   ["E9B0E15F-19D0-4721-A7E4-DB6C0B220FB4"],
        "roles": list(set(random.choices(dict0["roles"], k=random.randint(1, 3)))),
        "belongs": random.choice(dict0["belongs"]),
        "duration": {
            "slot": dict0["time_slot"][random.choice(list(dict0["time_slot"]))],
            "on_job": random.randint(10, 100),
            "last_rest": random.randint(0, 120)
        }
    }

    return {"returnVal": sampleStaffData}


if __name__ == "__main__":
    assets = main({})
    with open('../cloudant/assets_staff.json', 'w') as f:
        f.write(json.dumps(json.loads(assets['docs'])['docs']))

#     dataFormat = {
#   "type": "",
#   "id": "",
#   "roles": ["",""],
#   "belongs": "",
#   "duration": {
#     "on_job": 0,
#     "last_rest": 0
#   }
# }
