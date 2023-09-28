import quixstreams as qx
import os
import pandas as pd
from tqdm import tqdm


client = qx.QuixStreamingClient()

topic_consumer = client.get_topic_consumer(os.environ["input"], consumer_group = "empty-transformation")
gps_topic_producer = client.get_topic_producer(os.environ["gps_topic"])
gforce_topic_producer = client.get_topic_producer(os.environ["gforce_topic"])


def on_dataframe_received_handler(stream_consumer: qx.StreamConsumer, df: pd.DataFrame):
    
    topic_producer = gforce_topic_producer if "gForceX" in df else gps_topic_producer 

    stream_producer = topic_producer.get_or_create_stream(stream_id = stream_consumer.stream_id)
    stream_producer.timeseries.buffer.publish(df)

    pbar.update(df.shape[0])


def on_stream_received_handler(stream_consumer: qx.StreamConsumer):
    stream_consumer.timeseries.on_dataframe_received = on_dataframe_received_handler


# subscribe to new streams being received
topic_consumer.on_stream_received = on_stream_received_handler

print("Listening to streams. Press CTRL-C to exit.")

pbar = tqdm(unit="item", leave=True)

# Handle termination signals and provide a graceful exit
qx.App.run()