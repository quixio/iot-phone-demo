import os
from quixstreams import Application

# for local dev, load env vars from a .env file
from dotenv import load_dotenv
load_dotenv()

app = Application(consumer_group="transformation-v1", auto_offset_reset="earliest", use_changelog_topics=False)

input_topic = app.topic(os.environ["input"])
output_topic = app.topic(os.environ["output"])

sdf = app.dataframe(input_topic)

sdf = sdf.tumbling_window(5000, 5000).reduce(reduce_window, init_window).final()




sdf = sdf.apply(aggregate_window)

sdf.print()
#sdf.to_topic(output_topic)

if __name__ == "__main__":
    app.run()