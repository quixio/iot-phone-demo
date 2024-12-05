import os
import snowflake.connector

from quixstreams import Sink


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

    def write(self, record):
        insert_query = f"INSERT INTO {self.table} VALUES (%s, %s, %s)"
        self.cursor.execute(insert_query, (record.key, record.value, record.timestamp))
        self.conn.commit()