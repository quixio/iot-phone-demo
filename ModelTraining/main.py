import os
from threading import Thread
import influxdb_client_3 as InfluxDBClient3
from time import sleep

client = InfluxDBClient3.InfluxDBClient3(token=os.environ["INFLUXDB_TOKEN"],
                         host=os.environ["INFLUXDB_HOST"],
                         org=os.environ["INFLUXDB_ORG"],
                         database=os.environ["INFLUXDB_DATABASE"])


measurement_name = os.environ.get("INFLUXDB_MEASUREMENT_NAME")

try:
    # Query InfluxDB 3.0 usinfg influxql or sql
    table = client.query(query=f"SELECT * FROM \"gforce\" WHERE time >= now() - interval '1 hour'", language="influxql")

    # Convert the result to a pandas dataframe. Required to be processed through Quix. 
    df = table.to_pandas().drop(columns=["iox::measurement"])

    # If there are rows to write to the stream at this time
    print(df)

            
except Exception as e:
    print("query failed", flush=True)
    print(f"error: {e}",  flush=True)
    sleep(1)




