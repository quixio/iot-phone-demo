import os
from quixstreams import Application, State


app = Application.Quix("big-query-sink-v5", auto_offset_reset="latest")

input_topic = app.topic(os.environ["input"], value_deserializer="quix")
output_topic = app.topic(os.environ["output"], value_serializer="quix_timeseries")

sdf = app.dataframe(input_topic)

sdf.apply(lambda row, ctx: print(row))

sdf.to_topic(output_topic)

if __name__ == "__main__":
    app.run(sdf)