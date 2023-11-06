import os
from quixstreams import Application, State
from quixstreams.models.serializers.quix import QuixDeserializer, QuixTimeseriesSerializer

import pickle
import pandas as pd
from azure.storage.blob import BlobClient


model = "XGB_model_v1.8.pkl"
blob = BlobClient.from_connection_string(
    "DefaultEndpointsProtocol=https;AccountName=quixmodelregistry;AccountKey=9OkHZOhAW+1vtwWjReLKLQ8zyPzB0lDjaxjpTvIxaCrrlfe5rBehIc2NexmrrlyZoyUokfxlBkuaLUVUpoUoBQ==;EndpointSuffix=core.windows.net",
    "models",
    model,
)
loaded_model = pickle.load(open(model, "rb"))
with open(model, "wb+") as my_blob:
    print("Loading the model...")
    blob_data = blob.download_blob()
    blob_data.readinto(my_blob)
    print("Loaded")

def gForceTotalSum(row: dict, _, state: State):
    state_value = state.get("sum-1", 0.0)
    state_value += row["gForceTotal"]
    state.set("sum-1", state_value)
    row["sum"] = state_value

def predict(value: dict, _):
    data_df = pd.DataFrame(
        [
            {
                "gForceZ": value["gForceZ"],
                "gForceY": value["gForceY"],
                "gForceX": value["gForceX"],
                "gForceTotal": value["gForceTotal"],
            }
        ]
    )
    value["shaking"] = int(loaded_model.predict(data_df)[0])


app = Application.Quix("shake-detection-v1", auto_offset_reset="latest")

input_topic = app.topic(os.environ["input"], value_deserializer=QuixDeserializer())
output_topic = app.topic(os.environ["output"], value_serializer=QuixTimeseriesSerializer())

sdf = app.dataframe(input_topic)

sdf["gForceTotal"] = sdf["gForceX"].abs() + sdf["gForceY"].abs() + sdf["gForceZ"].abs()

sdf.apply(predict)
    
sdf.apply(lambda row, ctx: print(row))

sdf.to_topic(output_topic)

if __name__ == "__main__":
    app.run(sdf)