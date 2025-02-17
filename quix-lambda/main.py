import os
from quixstreams import Application
from function import process_microbatch
import pandas as pd

# for local dev, load env vars from a .env file
from dotenv import load_dotenv
load_dotenv()

app = Application(consumer_group="transformation-v1.1", auto_offset_reset="earliest")

input_topic = app.topic(os.environ["input"])
#output_topic = app.topic(os.environ["output"])

sdf = app.dataframe(input_topic)

sdf = sdf.tumbling_window(10000, 5000).collect().final()

sdf = sdf.apply(lambda row: process_microbatch(pd.DataFrame(row["value"])))
sdf = sdf.apply(lambda row: row.to_dict(orient='records'), expand=True)


sdf = sdf[sdf.contains("accelerometer-x")]
sdf = sdf[["time", "accelerometer-total", "accelerometer-x","accelerometer-y","accelerometer-z"]]

sdf.print()
#sdf.to_topic(output_topic)

if __name__ == "__main__":
    app.run()