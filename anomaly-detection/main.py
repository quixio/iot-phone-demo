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

app = Application(consumer_group="anomalies-v1.1", auto_offset_reset="earliest")

input_topic = app.topic(os.environ["input"])
output_topic = app.topic(os.environ["output"])

columns = ["Accelerometer-Disp-X", "Accelerometer-Disp-Y","Accelerometer-Disp-Z"]

sdf = app.dataframe(input_topic)

sdf = sdf.filter(lambda row: all(map(lambda c: c in row, columns)))

sdf["Accelerometer-Disp-total"] = sdf["Accelerometer-Disp-X"] + sdf["Accelerometer-Disp-Y"] + sdf["Accelerometer-Disp-Z"]

sdf = sdf.apply(last_row, stateful=True)

sdf = sdf[sdf.contains("last_row")]
sdf["diff"] = sdf["Accelerometer-Disp-total"] - sdf["last_row"]["Accelerometer-Disp-total"]

sdf = sdf.hopping_window(9000, 3000).reduce(lambda window, row: {
        "sum": window["sum"] + abs(row["diff"]),
        "device_id": row["device_id"],
        "location": row["location"]
    },lambda row: {
        "sum": row["diff"],
        "device_id": row["device_id"],
        "location": row["location"]
    }).final()

sdf = sdf[sdf["value"]["sum"] > 10]

sdf = sdf.apply(lambda row: {
    "title": "Anomaly detected",
    "message": f"Accelerometer {row['value']['device_id']} value changed by {row['value']['sum']} in last 5 seconds",
    "device_id": row["value"]["device_id"],
    "location": row["value"]["location"]
})

sdf.print()
sdf.to_topic(output_topic)

if __name__ == "__main__":
    app.run()