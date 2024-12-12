import os
from quixstreams import Application, State

# for local dev, load env vars from a .env file
from dotenv import load_dotenv
load_dotenv()

def last_row(row: dict, state: State):
    last_row_value = state.get("last_row", None)
    
    state.set("last_row", row)
    
    if last_row_value is not None:
        row["last_row"] = last_row_value
    return row

app = Application(consumer_group="transformation-v1", auto_offset_reset="earliest")

input_topic = app.topic(os.environ["input"])
output_topic = app.topic(os.environ["output"])

sdf = app.dataframe(input_topic)

sdf = sdf[sdf.contains("Accelerometer-Disp-X")]

sdf["Accelerometer-Disp-total"] = sdf["Accelerometer-Disp-X"] + sdf["Accelerometer-Disp-Y"] + sdf["Accelerometer-Disp-Z"]

sdf = sdf.apply(last_row, stateful=True)

sdf = sdf[sdf.contains("last_row")]
sdf["diff"] = sdf["Accelerometer-Disp-total"] - sdf["last_row"]["Accelerometer-Disp-total"]


sdf.print()
#sdf.to_topic(output_topic)

if __name__ == "__main__":
    app.run()