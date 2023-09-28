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
from sklearn.metrics import accuracy_score
from xgboost import XGBClassifier
import tensorflow as tf
import pickle
from azure.storage.blob import BlobServiceClient, BlobClient

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

print("Loading data from InfluxDb...")

df = query_influx(query_training)
df_test = query_influx(query_testing)

print("Data loaded.")

df["gForceTotal"] = df["gForceX"].abs() +  df["gForceY"].abs() + df["gForceZ"].abs()
df_test["gForceTotal"] = df_test["gForceX"].abs() +  df_test["gForceY"].abs() + df_test["gForceZ"].abs()

X_train = df[['gForceZ', 'gForceY', 'gForceX', 'gForceTotal']]
y_train = (df["TAG__team"]=="shaking").astype(int)

X_test = df_test[['gForceZ', 'gForceY', 'gForceX', 'gForceTotal']]
y_test = (df_test["TAG__team"]=="shaking").astype(int)



model = tf.keras.models.Sequential([
  tf.keras.layers.Flatten(input_shape=(X_train.shape[1],)),
  tf.keras.layers.Dense(50, activation='relu'),
  tf.keras.layers.Dense(50, activation='relu'),
  tf.keras.layers.Dense(1, activation='sigmoid')
])

model.compile(optimizer='sgd',
              loss='binary_crossentropy',
              metrics=['accuracy'])

model.summary()

model.fit(X_train, y_train, epochs=5)
model.evaluate(X_test,  y_test, verbose=2)


xgb_model = XGBClassifier()
xgb_model = xgb_model.fit(X=X_train, y=y_train)

y_pred_train = xgb_model.predict(X_train)
y_pred_test = xgb_model.predict(X_test)

ac_train = round(accuracy_score(y_train, y_pred_train), 4)
print('Train set precission :', ac_train)

ac_test = round(accuracy_score(y_test, y_pred_test), 4)
print('Test set precission :', ac_test)


df["PRED"] = xgb_model.predict(X_train)
df_test["PRED"] = xgb_model.predict(X_test)

# save the model to disk
filename = 'XGB_model_'+ version + '.pkl'
pickle.dump(xgb_model, open(filename, 'wb'))


blob = BlobClient.from_connection_string(
    "DefaultEndpointsProtocol=https;AccountName=quixmodelregistry;AccountKey=9OkHZOhAW+1vtwWjReLKLQ8zyPzB0lDjaxjpTvIxaCrrlfe5rBehIc2NexmrrlyZoyUokfxlBkuaLUVUpoUoBQ==;EndpointSuffix=core.windows.net",
    "models",
    filename)


with open(filename, "rb") as data:
    blob.upload_blob(data)