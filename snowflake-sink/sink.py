import os
import snowflake.connector
from quixstreaming import *


# Gets the info to connect to snowflake
SNOWFLAKE_ACCOUNT = os.environ["SNOWFLAKE_ACCOUNT"]
SNOWFLAKE_USER = os.environ["SNOWFLAKE_USER"]
SNOWFLAKE_PASSWORD = os.environ["SNOWFLAKE_PASSWORD"]
DATABASE = os.environ["DATABASE"]
SCHEMA = os.environ["SCHEMA"]
WAREHOUSE = os.environ["WAREHOUSE"]


class SnowflakeSink:

    def __init__(self):
        # Establish a connection to snowflake
        self.conn = snowflake.connector.connect(
            user=SNOWFLAKE_USER,
            password=SNOWFLAKE_PASSWORD,
            account=SNOWFLAKE_ACCOUNT,
            warehouse=WAREHOUSE,
            database=DATABASE,
            schema=SCHEMA
        )

    def write(self, dataframe):
        # write the dataframe to snowflake
        dataframe.write.jdbc(url=self.conn, name='my_table', mode='overwrite')

    def close(self):
        # Close the connection to snowflake
        self.conn.close()