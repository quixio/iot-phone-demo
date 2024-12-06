import os
from setup_logger import logger

from quixstreams import Application

# for local dev, load env vars from a .env file
from dotenv import load_dotenv
load_dotenv()

from sink import SnowflakeSink

TABLE_NAME = os.environ["TABLE_NAME"].strip()
DATABASE = os.environ["DATABASE"].strip()
SCHEMA = os.environ["SCHEMA"].strip()
USER = os.environ["USER"].strip()
PASSWORD = os.environ["PASSWORD"].strip()
ACCOUNT = os.environ["ACCOUNT"].strip().replace(' ', '').replace('+', '%2B')  # Fixes URL encoding issue
WAREHOUSE = os.environ["WAREHOUSE"].strip()

snowflake_sink = SnowflakeSink(
    ACCOUNT,
    USER,
    PASSWORD,
    DATABASE,
    SCHEMA,
    WAREHOUSE,
    TABLE_NAME)

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
