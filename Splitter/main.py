import quixstreams as qx
import os
import pandas as pd


client = qx.QuixStreamingClient()

topic_consumer = client.get_topic_consumer(
    os.environ["input"], 
    consumer_group = "splitter",
    auto_offset_reset=qx.AutoOffsetReset.Earliest)

gps_topic_producer = client.get_topic_producer(os.environ["gps_topic"])
gforce_topic_producer = client.get_topic_producer(os.environ["gforce_topic"])


def on_dataframe_received_handler(stream_consumer: qx.StreamConsumer, df: pd.DataFrame):
    
    print(df["gForceX"])
    if "gForceX" in df:
        print(df.columns)
        g_force_data = df[df["gForceX"].notna()] 
    else:
        g_force_data = pd.DataFrame()
        
    gps_data = df[df["BatteryLevel"].notna()] if "BatteryLevel" in df else pd.DataFrame()

    if g_force_data.shape[0] > 0:
        gforce_topic_producer.create_stream(stream_consumer.stream_id).timeseries.publish(g_force_data)

    if gps_data.shape[0] > 0:
        gps_topic_producer.create_stream(stream_consumer.stream_id).timeseries.publish(gps_data)



def on_stream_received_handler(stream_consumer: qx.StreamConsumer):
    stream_consumer.timeseries.on_dataframe_received = on_dataframe_received_handler


# subscribe to new streams being received
topic_consumer.on_stream_received = on_stream_received_handler

print("Listening to streams. Press CTRL-C to exit.")

# Handle termination signals and provide a graceful exit
qx.App.run()