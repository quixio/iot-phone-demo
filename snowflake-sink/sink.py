import logging
import snowflake.connector

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

    def connect(self):
        self.conn = snowflake.connector.connect(
            user=self.user,
            password=self.password,
            account=self.account)

    def __del__(self):
        if self.conn:
            self.conn.close()

    def write(self, batch: SinkBatch):
        cursor = self.conn.cursor()
        try:
            for item in batch:
                cursor.execute(
                    f'INSERT INTO {self.database}.{self.schema}.{self.table} VALUES (%s)',
                    (item.value,)
                )
        finally:
            cursor.close()