import os
from quixstreams import Application

# for local dev, load env vars from a .env file
from dotenv import load_dotenv
load_dotenv()

app = Application(consumer_group="telegraf-norm-v1", auto_offset_reset="earliest")

input_topic = app.topic(os.environ["input"])
output_topic = app.topic(os.environ["output"])

sdf = app.dataframe(input_topic)

def normalize(row: dict):

    output_row = {
        "timestamp": row["timestamp"],
    }
    
    for key, value in row["fields"].items():
        parameter_dimension = key.replace("values_", "")
        name = row["tags"]["name"]
        output_row[name + "-" + parameter_dimension] = value

    return output_row


sdf = sdf.apply(normalize)

sdf = sdf.hopping_window(5000, 250).reduce(lambda state, row: { **state, **row}, lambda row: row).final()

sdf = sdf.apply(lambda row:{
    "timestamp": row["start"],
    **row["value"]
})

sdf.print()

sdf.to_topic(output_topic)

if __name__ == "__main__":
    app.run()