import quixstreams as qx
from sdk.stream_reader_new import StreamReaderNew
from sdk.stream_writer_new import StreamWriterNew
import os
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

def predict(row):
      return loaded_model.predict(row[["gForceZ","gForceY","gForceX","gForceTotal"]].to_pandas_series())[0]


client = qx.QuixStreamingClient()

print("Opening input and output topics")

input_topic = client.get_topic_consumer(os.environ["input"], "v3.4", auto_offset_reset=qx.AutoOffsetReset.Latest)
output_topic = client.get_topic_producer(os.environ["output"])

async def on_new_stream(input_stream: StreamReaderNew, output_stream: StreamWriterNew):
    print("New stream: " + input_stream.stream_id)

    df = input_stream.df[["gForceX", "gForceY", "gForceZ"]]

    df = df[df["gForceX"] != None]

    df["gForceTotal"] = df.apply(lambda x: abs(x["gForceX"]) +  abs(x["gForceY"]) +  abs(x["gForceZ"]) )

    df["gForceTotal_5s"] = df["gForceTotal"].rolling("5s").mean()

    df["shaking"] = df.apply(predict)

    df.set_columns_print_width(10)

    print(df.header)

    async for row in df:
        print(row)
        await output_stream.write(row)



StreamReaderNew.process_stream(input_topic, output_topic, on_new_stream)

print("Listening to streams. Press CTRL-C to exit.")
qx.App.run()
