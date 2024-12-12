import os
from quixstreams import Application

# for local dev, load env vars from a .env file
from dotenv import load_dotenv
load_dotenv()

app = Application(consumer_group="transformation-v1", auto_offset_reset="earliest")

input_topic = app.topic(os.environ["input"])
output_topic = app.topic(os.environ["output"])

sdf = app.dataframe(input_topic)

sdf["Accelerometer-Disp-total"] = sdf["Accelerometer-Disp-X"] + sdf["Accelerometer-Disp-Y"] + sdf["Accelerometer-Disp-Z"]


sdf.print()
#sdf.to_topic(output_topic)

if __name__ == "__main__":
    app.run()