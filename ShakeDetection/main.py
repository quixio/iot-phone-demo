import quixstreams as qx
import os
import pandas as pd
from azure.storage.blob import BlobClient
import pickle

blob = BlobClient.from_connection_string(
    "DefaultEndpointsProtocol=https;AccountName=quixmodelregistry;AccountKey=9OkHZOhAW+1vtwWjReLKLQ8zyPzB0lDjaxjpTvIxaCrrlfe5rBehIc2NexmrrlyZoyUokfxlBkuaLUVUpoUoBQ==;EndpointSuffix=core.windows.net",
    "models",
    "XGB_model.pkl")

with open("XGB_model.pkl", "wb+") as my_blob:
    blob_data = blob.download_blob()
    blob_data.readinto(my_blob)
loaded_model = pickle.load(open("XGB_model.pkl", 'rb'))


client = qx.QuixStreamingClient()

print("Opening input and output topics")

input_topic = client.get_topic_consumer(os.environ["input"], "v3.4", auto_offset_reset=qx.AutoOffsetReset.Latest)
output_topic = client.get_topic_producer(os.environ["output"])


def on_dataframe_received(stream_consumer: qx.StreamConsumer, df: pd.DataFrame):
    
    if "gForceX" in df: 
        df["gForceTotal"] = df["gForceX"].abs() + df["gForceY"].abs() + df["gForceZ"].abs()
        df["shaking"] = loaded_model.predict(df[["gForceZ","gForceY","gForceX","gForceTotal"]])[0]

        print(df[["gForceTotal", "shaking"]])

        output_topic.get_or_create_stream(stream_consumer.stream_id).timeseries.publish(df)



def on_stream_received(stream_consumer: qx.StreamConsumer):
    print("New stream: " + stream_consumer.stream_id)

    stream_consumer.timeseries.on_dataframe_received = on_dataframe_received


input_topic.on_stream_received = on_stream_received


print("Listening to streams. Press CTRL-C to exit.")
qx.App.run()
