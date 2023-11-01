
#from quix_function import QuixFunction
import os
from streamingdataframes import Application, MessageContext, State
from streamingdataframes.models.rows import Row
from streamingdataframes.models.serializers import (
    QuixTimeseriesSerializer,
    QuixDeserializer,
    JSONDeserializer
)
import signal
from azure.storage.blob import BlobClient
import pickle
import pandas as pd

model = os.environ["model"]

blob = BlobClient.from_connection_string(
    "DefaultEndpointsProtocol=https;AccountName=quixmodelregistry;AccountKey=9OkHZOhAW+1vtwWjReLKLQ8zyPzB0lDjaxjpTvIxaCrrlfe5rBehIc2NexmrrlyZoyUokfxlBkuaLUVUpoUoBQ==;EndpointSuffix=core.windows.net",
    "models",
    model)

with open(model, "wb+") as my_blob:
    blob_data = blob.download_blob()
    blob_data.readinto(my_blob)

print("Loaded")

loaded_model = pickle.load(open(model, 'rb'))

# Quix app has an option to auto create topics
# Quix app does not require the broker being defined
app = Application.Quix("big-query-sink-v3", auto_offset_reset="earliest", )
input_topic = app.topic(os.environ["input"], value_deserializer=QuixDeserializer())
output_topic = app.topic(os.environ["output"], value_serializer=QuixTimeseriesSerializer())



def print_row(row: Row, ctx: MessageContext):
    print(row)


# Hook up to termination signal (for docker image) and CTRL-C
print("Listening to streams. Press CTRL-C to exit.")

def fill_gaps(value, ctx):
    if 'gForceX' not in value:
        value["gForceX"] = None
        value["gForceY"] = None
        value["gForceZ"] = None


def rolling_window(value: dict, ctx: MessageContext, state: State):
    
    state_value = state.get("rolling_10s", {})
    state_value = {int(k): v for k,v in state_value.items()}

    state_value[value["Timestamp"]] = value["gForceTotal"]
    timestamps = state_value.keys()
    last_timestamp = max(timestamps)
    filtered_window = {}
    for key in state_value:
        if (last_timestamp - key) < 10000000000:
            filtered_window[key] = state_value[key]
    
    state.set("rolling_10s", filtered_window)

    value["gForceTotal_10s"] = sum(filtered_window.values()) / len(filtered_window)
    df = pd.DataFrame([value["gForceZ"], value["gForceY"], value["gForceX"],value["gForceTotal"]], columns=['gForceZ', 'gForceY', 'gForceX', 'gForceTotal'])
    value["shaking"] = loaded_model.predict(df)



# "Gold" members get realtime notifications about purchase events larger than $1000
sdf = app.dataframe(topics_in=[input_topic])
sdf = sdf.apply(fill_gaps)
sdf = sdf[sdf["gForceX"].isnot(None)]
sdf = sdf[["Timestamp", "gForceX", "gForceY", "gForceZ"]]

sdf["gForceTotal"] = sdf["gForceX"] + sdf["gForceY"] + sdf["gForceZ"]
sdf.apply(rolling_window, stateful=True)
sdf.apply(print_row)  # easy way to print out

sdf.to_topic(output_topic)

signal.signal(signal.SIGINT, lambda _,_2: print("SIGINT"))
signal.signal(signal.SIGTERM, lambda _,_2: print("SIGTERM"))

try:
    app.run(sdf)
finally:
    print("Gracefully shutdowned.")