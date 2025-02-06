import os
from quixstreams import Application
from quixstreams.sinks.base.item import SinkItem
from quixstreams.sinks.community.mongodb import MongoDBSink

app = Application(consumer_group="mongodb-sink")
topic = app.topic(os.environ["input"])

# Message structured as:
# key: "CID_12345"
# value: {"name": {"first": "John", "last": "Doe"}, "age": 28, "city": "Los Angeles"}

def match_id(batch_item: SinkItem):
    return {"_id": f"{batch_item.key}_{batch_item.timestamp}"}

# Configure the sink
mongodb_sink = MongoDBSink(
    url="mongodb://mongodb:27017",
    db="sensordata",
    collection="sensordata",
    document_matcher=match_id
)

sdf = app.dataframe(topic=topic)
sdf.sink(mongodb_sink)

# MongoDB Document: 
# {"_id": "CID_12345", "name": {"first": "John", "last": "Doe"}, "age": 28, "city": "Los Angeles"}

if __name__ == "__main__":
    app.run()