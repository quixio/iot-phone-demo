import quixstreams as qx
import os
import pandas as pd
from azure.storage.blob import BlobClient
import pickle

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

client = qx.QuixStreamingClient()

print("Opening input and output topics")

input_topic = client.get_topic_consumer(os.environ["input"], "v6", auto_offset_reset=qx.AutoOffsetReset.Earliest)
output_topic = client.get_topic_producer(os.environ["output"])


def on_dataframe_received(stream_consumer: qx.StreamConsumer, df: pd.DataFrame):
    
    if "gForceX" in df: 
        df["gForceTotal"] = df["gForceX"].abs() + df["gForceY"].abs() + df["gForceZ"].abs()
        res = loaded_model.predict(df[["gForceZ","gForceY","gForceX","gForceTotal"]])
        df["shaking"] = res
        print(res)
        print(df[["gForceTotal", "shaking"]])

        output_topic.get_or_create_stream(stream_consumer.stream_id).timeseries.publish(df)



def on_stream_received(stream_consumer: qx.StreamConsumer):
    print("New stream: " + stream_consumer.stream_id)

    stream_consumer.timeseries.on_dataframe_received = on_dataframe_received




 

  


input_topic.on_stream_received = on_stream_received


print("Listening to streams. Press CTRL-C to exit.")
qx.App.run()
