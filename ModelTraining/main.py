# Importing necessary libraries and modules
import quixstreams as qx
import os
from threading import Thread
import influxdb_client_3 as InfluxDBClient3
from time import sleep

# Helper function to convert time intervals (like 1h, 2m) into seconds for easier processing.
# This function is useful for determining the frequency of certain operations.
def interval_to_seconds(interval):
    if not interval:
        raise ValueError("Invalid interval string")

    unit = interval[-1].lower()
    try:
        value = int(interval[:-1])
    except ValueError:
        raise ValueError("Invalid interval format")

    if unit == 's':
        return value
    elif unit == 'm':
        return value * 60
    elif unit == 'h':
        return value * 3600
    elif unit == 'd':
        return value * 3600 * 24
    elif unit == 'mo':
        return value * 3600 * 24 * 30
    elif unit == 'y':
        return value * 3600 * 24 * 365
    else:
        raise ValueError(f"Unknown interval unit: {unit}")


# should the main loop run?
# Global variable to control the main loop's execution
run = True

# Quix provides automatic credential injection for the client.
# However, if needed, the SDK token can be provided manually.
# Alternatively, you can always pass an SDK token manually as an argument.
client = qx.QuixStreamingClient()


client = InfluxDBClient3.InfluxDBClient3(token=os.environ["INFLUXDB_TOKEN"],
                         host=os.environ["INFLUXDB_HOST"],
                         org=os.environ["INFLUXDB_ORG"],
                         database=os.environ["INFLUXDB_DATABASE"])


measurement_name = os.environ.get("INFLUXDB_MEASUREMENT_NAME")

try:
    # Query InfluxDB 3.0 usinfg influxql or sql
    table = client.query(query=f"SELECT * FROM {measurement_name} WHERE time >= now() - {interval}", language="influxql")

    # Convert the result to a pandas dataframe. Required to be processed through Quix. 
    df = table.to_pandas().drop(columns=["iox::measurement"])

    # If there are rows to write to the stream at this time
    print(df)

            
except Exception as e:
    print("query failed", flush=True)
    print(f"error: {e}",  flush=True)
    sleep(1)




