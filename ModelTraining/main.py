import os
from threading import Thread
import influxdb_client_3 as InfluxDBClient3
from time import sleep
import pandas as pd
import requests
import io
import os
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

client = InfluxDBClient3.InfluxDBClient3(token=os.environ["INFLUXDB_TOKEN"],
                         host=os.environ["INFLUXDB_HOST"],
                         org=os.environ["INFLUXDB_ORG"],
                         database=os.environ["INFLUXDB_DATABASE"])


measurement_name = os.environ.get("INFLUXDB_MEASUREMENT_NAME")

def query_influx(query: str):
    # Query InfluxDB 3.0 usinfg influxql or sql
    table = client.query(query=query)

    df = table.to_pandas()
    # If there are rows to write to the stream at this time
    return df

            
version = os.environ["version"]
training_stream_ids = os.environ["training"].split(",")
training_stream_ids_query = str.join(",", list(map(lambda x: '\'' + x + '\'', training_stream_ids)))

testing_stream_ids = os.environ["testing"].split(",")
testing_stream_ids_query = str.join(",", list(map(lambda x: '\'' + x + '\'', training_stream_ids)))



query_training = f"SELECT * FROM \"gforce\" WHERE \"stream_id\" IN ({training_stream_ids_query})"
query_testing = f"SELECT * FROM \"gforce\" WHERE \"stream_id\" IN ({testing_stream_ids_query})"

print(query_training)



