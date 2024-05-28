import os
from quixstreams import Application, message_key

import json
import uuid
import datetime

# for local dev, load env vars from a .env file
from dotenv import load_dotenv
load_dotenv()

app = Application(consumer_group="data-norm-v1" + os.environ["period"], auto_offset_reset="earliest")

input_topic = app.topic(os.environ["input"])
output_topic = app.topic(os.environ["output"])

def transpose(row:dict):

    new_row = {
        "time": row["time"]
    }

    for key in row["values"]:
        new_row[row["name"] + "-" + key] = row["values"][key]

    return new_row

sdf = app.dataframe(input_topic)

sdf = sdf.apply(lambda message: message["payload"], expand=True)

sdf = sdf.apply(transpose)

sdf = sdf.hopping_window(10000, int(os.environ["period"]), 500).reduce(lambda state, row: {**state, **row}, lambda row: row).final()

sdf = sdf.apply(lambda row: {
    **row["value"],
    "time": row["end"]
})

sdf["datetime"] = sdf["time"].apply(lambda epoch: str(datetime.datetime.fromtimestamp(epoch/1000)))

sdf["time"] = sdf["time"] * 1000000

sdf["tags"] = sdf.apply(lambda _: {
    "session_id": bytes.decode(message_key())
})

sdf = sdf.update(lambda row: print(json.dumps(row, indent=4)))

sdf = sdf.to_topic(output_topic)

if __name__ == "__main__":
    app.run(sdf)