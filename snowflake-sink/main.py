import os
from setup_logger import logger

from quixstreams import Application

# for local dev, load env vars from a .env file
from dotenv import load_dotenv
load_dotenv()

from sink import SnowflakeSink  # Replaced BigQuerySink with SnowflakeSink

TABLE_NAME = os.environ["TABLE_NAME"]
DATABASE = os.environ["DATABASE"]
SCHEMA = os.environ["SCHEMA"]
WAREHOUSE = os.environ["WAREHOUSE"]
USER = os.environ["USER"]
PASSWORD = os.environ["PASSWORD"]
ACCOUNT = os.environ["ACCOUNT"]

snowflake_sink = SnowflakeSink(
    ACCOUNT,
    USER,
    PASSWORD,
    DATABASE,
    SCHEMA,
    WAREHOUSE,
    TABLE_NAME,
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
