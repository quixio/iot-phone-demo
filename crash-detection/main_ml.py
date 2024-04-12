import os
from quixstreams import Application, message_key
import json
import pandas as pd
import pickle

# for local dev, load env vars from a .env file
from dotenv import load_dotenv
load_dotenv()

# Load ML model from file.
model_pickle_path = 'my_model.pkl'
with open(model_pickle_path, 'rb') as file:
    loaded_model = pickle.load(file)

print("Model loaded from pickle file:")


app = Application(consumer_group="crash-prediction-ml-v2", auto_offset_reset="latest", use_changelog_topics=False)

input_topic = app.topic(os.environ["input"], timestamp_extractor=lambda row, *_: int(row["timestamp"] / 1000000))
output_topic = app.topic(os.environ["output"])

sdf = app.dataframe(input_topic)

# Filter rows that only contains GPS location and accelerometer at the same time.
sdf = sdf[sdf.contains("location-latitude") & sdf.contains("accelerometer-x")]

# We aggregate last 5s worth of data and emit batch every 1s to call ML model.
sdf = sdf.hopping_window(5000, 1000).reduce(lambda state, row: state + [row], lambda row: [row]).final()

# Call ML model to predict crash based on batch of sensor data. 
def predict(row: dict):
    # Aggregated batch from window operation.
    df = pd.DataFrame(row["value"])
    
    # We call ML model with expected columns.
    res = loaded_model.predict(df[["accelerometer-x","accelerometer-y", "accelerometer-z"]])
    
    # If there is any crash detected in window, we flag the window as crash.
    row["crash"] = int(max(res)) 
    
    # We set timestamp of the crash to the end of the window.
    row["timestamp"] = row["end"]       
    
    return row 

sdf = sdf.update(print)

sdf = sdf.apply(predict)

# We filter only windows where crash was detected.
sdf = sdf[sdf["crash"] == 1]

# We generate alert for the crash. 
sdf = sdf.apply(lambda row: {
    "alert": {
        "title": "Crash detected",
        "id": "crash",
      
        "timestamp": row["timestamp"],
        "location": {
            "latitude": row["value"][-1]["location-latitude"],
            "longitude": row["value"][-1]["location-longitude"],
        }
    }
})

# Count number of alerts in the window.
def count_alerts(state: dict, row: dict):
    state["count"] += 1
    state["alert"] = row
    
    return state

# We count alerts to send only first one.
sdf = sdf.tumbling_window(15000).reduce(count_alerts, lambda row: count_alerts({"count": 0}, row)).current()

# Take only first alert.
sdf = sdf[sdf["value"]["count"] == 1]

sdf = sdf.apply(lambda row: row["value"]["alert"])

sdf = sdf.update(lambda row: print(json.dumps(row, indent=4)))

sdf = sdf.to_topic(output_topic)

if __name__ == "__main__":
    app.run(sdf)