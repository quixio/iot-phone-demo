import logging
import snowflake.connector
import json

from quixstreams import Application

from quixstreams.exceptions import QuixException
from quixstreams.sinks import BatchingSink, SinkBatch

class SnowflakeSinkException(QuixException): ...

class SnowflakeSink(BatchingSink):
    def __init__(
        self,
        account: str,
        user: str,
        password: str,
        database: str,
        schema: str,
        warehouse: str,
        table: str,
        logger: logging.Logger
    ):
        super().__init__()
        self.account = account
        self.user = user
        self.password = password
        self.database = database
        self.schema = schema
        self.warehouse = warehouse
        self.table = table
        self.logger = logger
        self.conn = None

    def connect(self):
        self.conn = snowflake.connector.connect(
        user=self.user,
        password=self.password,
        account=self.account,  # Replace with your correct account and region
        database=self.database,
        schema=self.schema,
        warehouse=self.warehouse
    )

    def disconnect(self):
        if self.conn:
            self.conn.close()
            self.conn = None

    def write(self, batch: SinkBatch):
        cursor = self.conn.cursor()
        try:
            for item in batch:
                # Update point: Converting dictionary to a JSON formatted string
                json_value = json.dumps(item.value)
                cursor.execute(
                    f'INSERT INTO {self.database}.{self.schema}.{self.table} VALUES (%s)',
                    (json_value,)
                )
        finally:
            cursor.close()