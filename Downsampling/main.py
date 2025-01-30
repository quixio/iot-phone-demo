import os
from quixstreams import Application
from downsampling import reduce_window, init_window, aggregate_window

# for local dev, load env vars from a .env file
from dotenv import load_dotenv
load_dotenv()

window_size_s = os.environ["window_size_s"]

app = Application(consumer_group=f"downsampling-{window_size_s}-v1", auto_offset_reset="earliest", use_changelog_topics=False)

input_topic = app.topic(os.environ["input"])
output_topic = app.topic(os.environ["output"])

sdf = app.dataframe(input_topic)

sdf = sdf.drop("timestamp")

sdf = sdf.tumbling_window(int(window_size_s) * 1000, 5000) \
    .reduce(reduce_window, init_window).final()

sdf = sdf.apply(aggregate_window)

#sdf.print()
sdf.to_topic(output_topic)

if __name__ == "__main__":
    app.run()