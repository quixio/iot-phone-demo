import os
from streamingdataframes import Application, MessageContext, State
from streamingdataframes.models.rows import Row
from streamingdataframes.models.serializers import (
    QuixTimeseriesSerializer,
    QuixDeserializer,
    JSONDeserializer
)
import signal

# Quix app does not require the broker being defined
app = Application.Quix("big-query-sink-v5", auto_offset_reset="latest", )
input_topic = app.topic(os.environ["input"], value_deserializer=QuixDeserializer())
output_topic = app.topic(os.environ["output"], value_serializer=QuixTimeseriesSerializer())

# Hook up to termination signal (for docker image) and CTRL-C



# "Gold" members get realtime notifications about purchase events larger than $1000
sdf = app.dataframe(input_topic)
sdf = sdf[["Timestamp", "gForceX", "gForceY", "gForceZ"]]

sdf["gForceTotal"] = sdf["gForceX"].abs() + sdf["gForceY"].abs() + sdf["gForceZ"].abs()

sdf["shaking"] = sdf["gForceTotal"] > 15 

def gForceTotalSum(row: dict, ctx, state: State):
    state_value = state.get("sum-1", 0)
    state_value += row["gForceTotal"]
    state.set("sum-1", state_value)
    return row

sdf["sum"] = sdf.apply(gForceTotalSum, stateful=True)



sdf.apply(lambda row,ctx: print(row))  # easy way to print out

#sdf.to_topic(output_topic)

print("Listening to streams. Press CTRL-C to exit.")
app.run(sdf)