import os
from quixstreams import Application, State
from quixstreams.models.serializers.quix import QuixDeserializer, QuixTimeseriesSerializer


app = Application.Quix("transformation-v1", auto_offset_reset="latest")

input_topic = app.topic(os.environ["input"], value_deserializer=QuixDeserializer())
output_topic = app.topic(os.environ["output"], value_serializer=QuixTimeseriesSerializer())

sdf = app.dataframe(input_topic)

sdf["gForceTotal"] = sdf["gForceX"].abs() + sdf["gForceY"].abs() + sdf["gForceZ"].abs()
sdf["shaking"] = sdf["gForceTotal"] > 15
sdf["shaking"] = sdf["shaking"].apply(lambda value, _: 1 if value else 0)

def sum_gForceTotal(row: dict, ctx, state: State):
    sum_value = state.get("sum", 0)
    sum_value += row["gForceTotal"]
    state.set("sum", sum_value)
    row["sum"] = sum_value
    
sdf.apply(sum_gForceTotal, stateful=True)
sdf = sdf[["shaking", "gForceTotal"]]

sdf.apply(lambda row, ctx: print(row))

#sdf.to_topic(output_topic)

if __name__ == "__main__":
    app.run(sdf)