import os
import snowflake.connector
import logging

from quixstreams.exceptions import QuixException


class SnowflakeSinkException(QuixException): ...


class SnowflakeSink:
    def __init__(self, user, password, warehouse, database, schema, logger):
        self.user = user
        self.password = password
        self.warehouse = warehouse
        self.database = database
        self.schema = schema
        self.logger = logger

        self.conn = None
        self.cursor = None

    def connect(self):
        self.conn = snowflake.connector.connect(
            user=self.user,
            password=self.password,
            warehouse=self.warehouse,
            database=self.database,
            schema=self.schema
        )
        self.cursor = self.conn.cursor()

        self.logger.info('Connected to Snowflake.')

    def write(self, data):
        for item in data:
            # Assuming data is a list of dictionaries
            keys = list(item.keys())
            values = list(item.values())

            query = f"INSERT INTO streaming_table ({', '.join(keys)}) VALUES ({', '.join('%s' for _ in values)})"
            self.cursor.execute(query, values)

        self.conn.commit()

    def close(self):
        self.conn.close()
        self.logger.info('Connection to Snowflake has been closed.')
