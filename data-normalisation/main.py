import os
from quixstreams import Application

# for local dev, load env vars from a .env file
from dotenv import load_dotenv
load_dotenv()

import json
import datetime
import uuid

app = Application(consumer_group="data-norm-v1", auto_offset_reset="latest", use_changelog_topics=False)

input_topic = app.topic(os.environ["input"])
output_topic = app.topic(os.environ["output"])

def transpose(row: dict):
    
    new_row = {
        "time": row["time"]
    }

    for key in row["values"]:
        new_row[row["name"] + "-" + key] = row["values"][key]

    return new_row

sdf = app.dataframe(input_topic)

sdf = sdf.apply(lambda message: message["payload"], expand=True)

sdf = sdf.apply(transpose)

sdf = sdf.set_timestamp(lambda row, _: int(row["time"] / 1E6))

sdf = sdf.hopping_window(10000, 1000, 500) \
        .reduce(lambda state, row: {**state, **row}, lambda row: row) \
        .final()

sdf = sdf.apply(lambda row: {
    **row["value"],
    "time": row["end"]
})


sdf["datetime"] = sdf["time"].apply(lambda epoch: str(datetime.datetime.fromtimestamp(epoch / 1000) ))
sdf["time"] = sdf["time"] * 1000000

sdf["tags"] = sdf.apply(lambda row, key, *_: {
    "session_id": bytes.decode(key)
}, metadata=True)

def update_floats(row: dict):
    if "location-horizontalAccuracy" in row:
        row["location-horizontalAccuracy"] = float(row["location-horizontalAccuracy"])

sdf = sdf.update(update_floats)

sdf = sdf.update(lambda row: print(json.dumps(row, indent=4)))

sdf = sdf.to_topic(output_topic)

if __name__ == "__main__":
    app.run(sdf)