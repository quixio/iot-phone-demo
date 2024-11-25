import os
from setup_logger import logger

from quixstreams import Application

# for local dev, load env vars from a .env file
from dotenv import load_dotenv
load_dotenv()

from sink import SnowflakeSink

ACCOUNT = os.environ["ACCOUNT"]
USER = os.environ["USER"]
PASSWORD = os.environ["PASSWORD"]
WAREHOUSE = os.environ["WAREHOUSE"]
DB = os.environ["DB"]
SCHEMA = os.environ["SCHEMA"]
TABLE = os.environ["TABLE"]
ROLE = os.environ["ROLE"]

snowflake_sink = SnowflakeSink(ACCOUNT, USER, PASSWORD, WAREHOUSE, DB, SCHEMA, TABLE, ROLE)

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
