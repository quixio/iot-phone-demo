import os
from quixstreams import Application

# for local dev, load env vars from a .env file
from dotenv import load_dotenv
load_dotenv()

app = Application(consumer_group="transformation-v1", auto_offset_reset="earliest")

input_topic = app.topic(os.environ["input"])
#output_topic = app.topic(os.environ["output"])

sdf = app.dataframe(input_topic)

sdf = sdf.tumbling_window(10000, 5000).collect().final()

def process_microbatch(row: dict):

    # Convert to DataFrame
    df = pd.DataFrame(data)

    # Display the DataFrame
    print(df)

    return df

sdf = sdf.apply(process_microbatch)

sdf.print()
#sdf.to_topic(output_topic)

if __name__ == "__main__":
    app.run()