import os
from quixstreams import Application

# for local dev, load env vars from a .env file
from dotenv import load_dotenv
load_dotenv()

app = Application(
    consumer_group="mqtt-norm-v1.2", 
    auto_offset_reset="earliest")

input_topic = app.topic(os.environ["input"], value_deserializer="bytes", key_deserializer="str")
output_topic = app.topic(os.environ["output"])


sdf = app.dataframe(input_topic)

# Filter out keys that don't have the correct format.
sdf = sdf.filter(lambda row, key, *_: key.startswith("MSU") and len(key.split("-")) == 6, metadata=True)

def expand_key(row, key, timestamp, headers):
    
    expanded_key = key.split("-")
    sensor_id = f"{expanded_key[1]}-{expanded_key[2]}-{expanded_key[3]}"
    
    

    result = {
        "device_id": expanded_key[4],
        "location": expanded_key[5],
        "timestamp": timestamp
    }
    
    value = bytes.decode(row)
    
    if isinstance(value, (int, float)):  # Check for number (integer or float)
        result[sensor_id] =  float(value)
    elif isinstance(value, str):  # Check for string
        try:
            # Attempt to parse the value as a number
            parsed_value = float(value)
            result[sensor_id] = float(parsed_value)
        except (ValueError, TypeError):
            # If parsing fails, assign as a string
            result[sensor_id] = str(value)
        
    return result

sdf = sdf.apply(expand_key, metadata=True)
sdf = sdf.group_by("device_id")
sdf = sdf.sliding_window(60000, 5000).reduce(lambda window, row: {**window, **row}, lambda row: row).final()

sdf = sdf.apply(lambda row: row["value"])
sdf = sdf.drop("timestamp")

sdf.print()
sdf.to_topic(output_topic)

if __name__ == "__main__":
    app.run()