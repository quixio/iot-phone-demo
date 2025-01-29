import os
from quixstreams import Application

# for local dev, load env vars from a .env file
from dotenv import load_dotenv
load_dotenv()

app = Application(consumer_group="transformation-v1", auto_offset_reset="earliest")

input_topic = app.topic(os.environ["input"])
output_topic = app.topic(os.environ["output"])

sdf = app.dataframe(input_topic)

def reduce_window(window:dict, row: dict):

    for key, value in row.items():

        if key == "timestamp":
            continue
        elif isinstance(value, (int, float)):
            if key not in window:
                window[key] = {
                    "sum": value,
                    "count": 1
                }
            else:
                window[key]["sum"] += value
                window[key]["count"] += 1
        else:
            window[key] = value

def init_window(window:dict, row: dict):

    for key, value in row.items():

        if key == "timestamp":
            continue
        elif isinstance(value, (int, float)):
            window[key] = {
                "sum": value,
                "count": 1
            }
        else:
            window[key] = value
    

sdf.print()
sdf.to_topic(output_topic)

if __name__ == "__main__":
    app.run()