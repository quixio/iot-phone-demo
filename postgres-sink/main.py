import os
from quixstreams import Application
from posgresql_sink import PostgresSink

# for local dev, load env vars from a .env file
from dotenv import load_dotenv
load_dotenv()

bigquery_sink = PostgresSink(
    host=os.environ["POSTGRES_HOST"],
    port=os.environ["POSTGRES_PORT"],
    dbname=os.environ["POSTGRES_DB"],
    user=os.environ["POSTGRES_USER"],
    password=os.environ["POSTGRES_PASSWORD"],
    table_name=os.environ["POSTGRES_TABLE_NAME"],
    schema_auto_update=True
)

app = Application(
    consumer_group=os.environ["CONSUMER_GROUP"], 
    auto_offset_reset = "earliest",
    commit_interval=1,
    commit_every=100)

input_topic = app.topic(os.environ["input"], key_deserializer="string")

sdf = app.dataframe(input_topic)
sdf.sink(bigquery_sink)

if __name__ == "__main__":
    app.run(sdf)