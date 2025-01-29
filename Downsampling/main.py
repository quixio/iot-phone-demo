import os
from quixstreams import Application

# for local dev, load env vars from a .env file
from dotenv import load_dotenv
load_dotenv()

app = Application(consumer_group="transformation-v1", auto_offset_reset="earliest", use_changelog_topics=False)

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
    
    return window

def init_window(row: dict):

    window = {}
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

    return window

sdf = sdf.tumbling_window(5000, 5000).reduce(reduce_window, init_window).final()

def aggregate_window(window: dict):
    result = {
        "timestamp": window["end"] * 1E6
    }

    for key, value in window["value"].items():

        if "sum" in value:
            result[key] = value["sum"] / value["count"]
        else:
            result[key] = value

    return result


sdf = sdf.apply(aggregate_window)

sdf.print()
#sdf.to_topic(output_topic)

if __name__ == "__main__":
    app.run()