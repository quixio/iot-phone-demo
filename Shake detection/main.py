from quixstreaming import QuixStreamingClient, AutoOffsetReset
from quixstreaming.app import App
from sdk.stream_reader_new import StreamReaderNew
from sdk.stream_writer_new import StreamWriterNew
import os

client = QuixStreamingClient()

print("Opening input and output topics")

input_topic = client.open_input_topic("phone-data", "v3", auto_offset_reset=AutoOffsetReset.Latest)
output_topic = client.open_output_topic("events")

async def on_new_stream(input_stream: StreamReaderNew, output_stream: StreamWriterNew):
    print("New stream: " + input_stream.stream_id)

    df = input_stream.df[["gForceX", "gForceY", "gForceZ"]]

    df = df[df["gForceX"] != None]

    df["gForceTotal"] = df.apply(lambda x: abs(x["gForceX"]) +  abs(x["gForceY"]) +  abs(x["gForceZ"]) )

    df["gForceTotal_10s"] = df["gForceTotal"].rolling("10s").mean()

    df["shaking"] = df.apply(lambda x: 1 if x["gForceTotal_10s"] > 15 else 0)

    df.set_columns_print_width(15)

    print(df.header)

    async for row in df:
        print(row)
        await output_stream.write(row)



StreamReaderNew.process_stream(input_topic, output_topic, on_new_stream)

print("Listening to streams. Press CTRL-C to exit.")
App.run()
