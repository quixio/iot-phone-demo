import os
from quixstreams import Application

import uuid
import json
import datetime
# for local dev, load env vars from a .env file
from dotenv import load_dotenv
load_dotenv()

app = Application(consumer_group=str(uuid.uuid4()), auto_offset_reset="earliest")

input_topic = app.topic(os.environ["input"])
output_topic = app.topic(os.environ["output"])

sdf = app.dataframe(input_topic)

sdf = sdf.apply(lambda row: row["payload"], expand=True)

def transpose(row: dict):
    
    new_row = {
        "time": row["time"]
    }
    
    for key in row["values"]:
        new_row[row["name"] + "-" + key] = row["values"][key]
        
    return new_row

sdf = sdf.apply(transpose)

# put transformation logic here
# see docs for what you can do
# https://quix.io/docs/get-started/quixtour/process-threshold.html

sdf = sdf.hopping_window(10000, 250, 1000).reduce(lambda state, row: {**state, **row}, lambda row: row).final()

sdf = sdf.apply(lambda row: {
    "time": row["start"],
    **row["value"]
})

#sdf["time"] = sdf["time"].apply(lambda epoch: str(datetime.datetime.fromtimestamp(epoch / 1E9)))


sdf = sdf[sdf.contains("accelerometer-x")]

sdf["accelerometer-total"] = sdf["accelerometer-x"].abs() + sdf["accelerometer-y"].abs() + sdf["accelerometer-z"].abs()

sdf = sdf[["time", "accelerometer-x", "accelerometer-y",  "accelerometer-z", "accelerometer-total"]]

sdf = sdf[sdf["accelerometer-x"] > 0]

sdf = sdf.update(lambda row: print(list(row.values())))

sdf = sdf.to_topic(output_topic)

if __name__ == "__main__":
    app.run(sdf)