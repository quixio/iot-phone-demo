import os
from setup_logger import logger
from dotenv import load_dotenv
from quixstreams import Application
from sink import SnowflakeSink

load_dotenv()

SNOWFLAKE_ACCOUNT = os.environ["SNOWFLAKE_ACCOUNT"]
SNOWFLAKE_USER = os.environ["SNOWFLAKE_USER"]
SNOWFLAKE_PASSWORD = os.environ["SNOWFLAKE_PASSWORD"]
DATABASE = os.environ["DATABASE"]
SCHEMA = os.environ["SCHEMA"]
WAREHOUSE = os.environ["WAREHOUSE"]

snowflake_sink = SnowflakeSink()

app = Application(
    consumer_group=os.environ["CONSUMER_GROUP"], 
    auto_offset_reset = "earliest",
    commit_interval=1,
    commit_every=100)

input_topic = app.topic(os.environ["input"])

sdf = app.dataframe(input_topic)

def write_to_sink(sdf):
    snowflake_sink.write(sdf)

sdf.sink(write_to_sink)

if __name__ == "__main__":
    app.run(sdf)
    snowflake_sink.close()