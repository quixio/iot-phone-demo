import os
from setup_logger import logger

from quixstreams import Application

# for local dev, load env vars from a .env file
from dotenv import load_dotenv
load_dotenv()

from sink import SnowflakeSink

TABLE_NAME = os.environ["TABLE_NAME"]
WAREHOUSE = os.environ["WAREHOUSE"]
DATABASE = os.environ["DATABASE"]
SCHEMA = os.environ["SCHEMA"]
ACCOUNT = os.environ["ACCOUNT"]
USER = os.environ["USER"]
PASSWORD = os.environ["PASSWORD"]

snowflake_sink = SnowflakeSink(
    WAREHOUSE, 
    DATABASE, 
    SCHEMA,
    TABLE_NAME, 
    ACCOUNT,
    USER,
    PASSWORD,
    logger)

snowflake_sink.connect()

app = Application(
    consumer_group=os.environ["CONSUMER_GROUP"], 
    auto_offset_reset = "earliest",
    commit_interval=1,
    commit_every=100)

input_topic = app.topic(os.environ["input"])

sdf = app.dataframe(input_topic)
sdf.sink(snowflake_sink)

if __name__ == "__main__":
    app.run(sdf)