import os
from quixstreams import Application
from quixstreams.sinks.community.mongodb import MongoDBSink

app = Application(broker_address="localhost:9092")
topic = app.topic("topic-name")

# Message structured as:
# key: "CID_12345"
# value: {"name": {"first": "John", "last": "Doe"}, "age": 28, "city": "Los Angeles"}

# Configure the sink
mongodb_sink = MongoDBSink(
    url="mongodb://mongodb:27017",
    db="sensor-data",
    collection="sensor-data",
)

sdf = app.dataframe(topic=topic)
sdf.sink(mongodb_sink)

# MongoDB Document: 
# {"_id": "CID_12345", "name": {"first": "John", "last": "Doe"}, "age": 28, "city": "Los Angeles"}

if __name__ == "__main__":
    app.run()