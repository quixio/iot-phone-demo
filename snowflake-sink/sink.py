import logging
import snowflake.connector

from quixstreams import Sink

logger = logging.getLogger(__name__)

class SnowflakeSink(Sink):
    def __init__(self, account, user, password, warehouse, database, schema, table, logger):
        self.account = account
        self.user = user
        self.password = password
        self.warehouse = warehouse
        self.database = database
        self.schema = schema
        self.table = table
        self.logger = logger

    def connect(self):
        self.conn = snowflake.connector.connect(
            user=self.user,
            password=self.password,
            account=self.account,
            warehouse=self.warehouse,
            database=self.database,
            schema=self.schema
        )
        self.cursor = self.conn.cursor()

    def write(self, batch):
        for item in batch:
            insert_query = f"INSERT INTO {self.table} VALUES ({', '.join(['%s'] * len(item.value))})"
            self.cursor.execute(insert_query, tuple(item.value.values()))

    def close(self):
        self.conn.close()