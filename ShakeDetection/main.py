import quixstreams as qx
from sdk.stream_reader_new import StreamReaderNew
from sdk.stream_writer_new import StreamWriterNew
import os
import pandas as pd

client = qx.QuixStreamingClient()

print("Opening input and output topics")

input_topic = client.get_topic_consumer(os.environ["input"], "v3.4", auto_offset_reset=qx.AutoOffsetReset.Latest)
output_topic = client.get_topic_producer(os.environ["output"])


def on_dataframe_received(stream_consumer: qx.StreamConsumer, df: pd.DataFrame):
    
    if "gForceX" in df: 
        df = df[["gForceX", "gForceY", "gForceZ"]]

        print(df)

    #df["gForceTotal"] = df.apply(lambda x: abs(x["gForceX"]) +  abs(x["gForceY"]) +  abs(x["gForceZ"]) )

    #df["shaking"] = df.apply(lambda x: 1 if x["gForceTotal"] > 15 else 0)

def on_stream_received(stream_consumer: qx.StreamConsumer):
    print("New stream: " + stream_consumer.stream_id)

    stream_consumer.timeseries.on_dataframe_received = on_dataframe_received




 

  


input_topic.on_stream_received = on_stream_received


print("Listening to streams. Press CTRL-C to exit.")
qx.App.run()
