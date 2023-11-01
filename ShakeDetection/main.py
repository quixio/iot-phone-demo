
#from quix_function import QuixFunction
import os
from streamingdataframes import Application, MessageContext, State
from streamingdataframes.models.rows import Row
from streamingdataframes.models.serializers import (
    QuixTimeseriesSerializer,
    QuixDeserializer,
    JSONDeserializer
)

# Quix app has an option to auto create topics
# Quix app does not require the broker being defined
app = Application.Quix("big-query-sink-v3", auto_offset_reset="earliest")
input_topic = app.topic(os.environ["input"], value_deserializer=QuixDeserializer())



def print_row(row: Row, ctx: MessageContext):
    print(row)


# Hook up to termination signal (for docker image) and CTRL-C
print("Listening to streams. Press CTRL-C to exit.")

def fill_gaps(value, ctx):
    if 'gForceX' not in value:
        value["gForceX"] = None
        value["gForceY"] = None
        value["gForceZ"] = None


def rolling_window(value: dict, ctx: MessageContext, state: State):
    
    state_value = state.get("rolling_10s", {})

    state_value[+value["Timestamp"]] = value["gForceTotal"]
    print(state_value)
    timestamps = state_value.keys()
    print(timestamps)
    last_timestamp = max(timestamps)
    filtered_window = {}
    for key in state_value:
        if (last_timestamp - key) < 10000000000:
            filtered_window[key] = state_value[key]
    
    print(filtered_window)
    state.set("rolling_10s", filtered_window)

    value["gForceTotal_10s"] = sum(filtered_window.values()) / len(filtered_window)



# "Gold" members get realtime notifications about purchase events larger than $1000
sdf = app.dataframe(topics_in=[input_topic])
sdf = sdf.apply(fill_gaps)
sdf = sdf[sdf["gForceX"].isnot(None)]
sdf = sdf[["Timestamp", "gForceX", "gForceY", "gForceZ"]]

sdf["gForceTotal"] = sdf["gForceX"] + sdf["gForceY"] + sdf["gForceZ"]
sdf.apply(rolling_window, stateful=True)
sdf = sdf.apply(print_row)  # easy way to print out


app.run(sdf)