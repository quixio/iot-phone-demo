import os
from quixstreams import Application
from dotenv import load_dotenv
from sink import SnowflakeSink

load_dotenv()

TABLE_NAME = os.environ["TABLE_NAME"]
USER = os.environ["USER"]
PASSWORD = os.environ["PASSWORD"]
ACCOUNT = os.environ["ACCOUNT"]
WAREHOUSE = os.environ["WAREHOUSE"]
DATABASE = os.environ["DATABASE"]
SCHEMA = os.environ["SCHEMA"]

snowflake_sink = SnowflakeSink(USER, PASSWORD, ACCOUNT, WAREHOUSE, DATABASE, SCHEMA, TABLE_NAME)
snowflake_sink.connect()

app = Application(consumer_group=os.environ["CONSUMER_GROUP"], auto_offset_reset = "earliest", commit_interval=1, commit_every=100)

input_topic = app.topic(os.environ["input"])

sdf = app.dataframe(input_topic)
sdf.sink(snowflake_sink)

if __name__ == "__main__":
    app.run(sdf)