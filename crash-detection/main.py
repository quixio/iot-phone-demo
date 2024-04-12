import os
from quixstreams import Application
import uuid
import json

# for local dev, load env vars from a .env file
from dotenv import load_dotenv
load_dotenv()

import pickle

model_pickle_path = 'my_model.pkl'
with open(model_pickle_path, 'rb') as file:
    loaded_model = pickle.load(file)

print("Model loaded from pickle file:")


app = Application(consumer_group=str(uuid.uuid4()), auto_offset_reset="earliest", use_changelog_topics=False)

input_topic = app.topic(os.environ["input"], timestamp_extractor=lambda row, *_: int(row["timestamp"] / 1000000))
output_topic = app.topic(os.environ["output"])

sdf = app.dataframe(input_topic)

sdf = sdf.hopping_window(5000, 250).reduce(lambda state, row: { **state, **row}, lambda row: row).final()

sdf = sdf.apply(lambda row:{
    "timestamp": row["start"],
    **row["value"]
})
sdf = sdf[sdf.contains("location-latitude") & sdf.contains("accelerometer-x")]


sdf["accelerometer-total-g"] = sdf["accelerometer-x"].abs() + sdf["accelerometer-y"].abs() +sdf["accelerometer-z"].abs()

def sum_forces(state: dict, row: dict):
    
    state["sum_forces"] += row["accelerometer-total-g"]
    state["count"] += 1
    
    state["location-latitude"] = row["location-latitude"]
    state["location-longitude"] = row["location-longitude"]
    
    state["payload"] = row
    
    return state 
    
def init_forces(row: dict):
    
    state = {
        "sum_forces" : 0,
        "count": 0
    }
    
    return sum_forces(state, row)


sdf = sdf.hopping_window(1000, 250).reduce(sum_forces, init_forces).final()

sdf = sdf[sdf["value"]["sum_forces"] / sdf["value"]["count"] > 25]



sdf = sdf.apply(lambda row: {
    "alert": {
        "title": "Crash detected",
        "timestamp": row["end"],
        "location": {
            "latitude": row["value"]["location-latitude"],
            "longitude": row["value"]["location-longitude"],
        }
    }
})




def count_alerts(state: dict, row: dict):
    state["count"] += 1
    state["alert"] = row
    
    return state

sdf = sdf.tumbling_window(60000).reduce(count_alerts, lambda row: count_alerts({"count": 0}, row)).current()

sdf = sdf[sdf["value"]["count"] == 1]

#sdf = sdf.update(lambda row: print(json.dumps(row, indent=4)))



#sdf = sdf.to_topic(output_topic)

if __name__ == "__main__":
    app.run(sdf)