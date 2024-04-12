import os
from quixstreams import Application

# for local dev, load env vars from a .env file
from dotenv import load_dotenv
load_dotenv()

app = Application(consumer_group="raw-to-table-v5", auto_offset_reset="latest", use_changelog_topics=False)

input_topic = app.topic(os.environ["input"])
output_topic = app.topic(os.environ["output"])

sdf = app.dataframe(input_topic)

sdf = sdf.apply(lambda row: row["payload"], expand=True)

def expand_values_to_columns(row: dict):
    new_row = {}
    for key in row["values"]:
        new_row[row["name"] + "-" + key] = row["values"][key]

    new_row["timestamp"] = row["time"]
    
    return new_row

sdf = sdf.apply(expand_values_to_columns)

sdf = sdf.hopping_window(5000, 250).reduce(lambda state, row: { **state, **row}, lambda row: row).final()

sdf = sdf.apply(lambda row:{
    "timestamp": row["start"],
    **row["value"]
})

sdf = sdf.update(lambda row: print(row))

sdf = sdf.to_topic(output_topic)

if __name__ == "__main__":
    app.run(sdf)