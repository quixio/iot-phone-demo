import os
from quixstreams import Application
import uuid

# for local dev, load env vars from a .env file
from dotenv import load_dotenv
load_dotenv()

app = Application(
    quix_sdk_token="sdk-cee8f09781be43a8867a4e33cb8f3929", 
    consumer_group=str(uuid.uuid4()), 
    auto_offset_reset="earliest", 
    use_changelog_topics=False)

input_topic = app.topic("raw")
#output_topic = app.topic(os.environ["output"])

sdf = app.dataframe(input_topic)

# put transformation logic here
# see docs for what you can do
# https://quix.io/docs/get-started/quixtour/process-threshold.html

sdf = sdf.update(lambda row: print(row))

#sdf = sdf.to_topic(output_topic)

if __name__ == "__main__":
    app.run(sdf)