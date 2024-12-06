import logging
import snowflake.connector

from quixstreams import Sink

logger = logging.getLogger(__name__)

class SnowflakeSink(Sink):
    def __init__(self, account, user, password, role, warehouse, database, schema, table, logger):
        self.account = account
        self.user = user
        self.password = password
        self.role = role
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
            schema=self.schema,
            role=self.role,
        )
        self.cursor = self.conn.cursor()

    def write(self, batch):
        for item in batch:
            self.cursor.execute(
                f"INSERT INTO {self.table} VALUES (%s, %s, %s)",
                (item.key, item.value, item.timestamp)
            )
        self.conn.commit()