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
        df["gForceTotal"] = df["gForceX"].abs() + df["gForceY"].abs() + df["gForceZ"].abs()
        df["shaking"] = df["gForceTotal"].apply(lambda x: 1 if x > 15 else 0)

        print(df[["gForceTotal", "shaking"]])

        output_topic.get_or_create_stream(stream_consumer.stream_id).timeseries.publish(df)



def on_stream_received(stream_consumer: qx.StreamConsumer):
    print("New stream: " + stream_consumer.stream_id)

    stream_consumer.timeseries.on_dataframe_received = on_dataframe_received




 

  


input_topic.on_stream_received = on_stream_received


print("Listening to streams. Press CTRL-C to exit.")
qx.App.run()
