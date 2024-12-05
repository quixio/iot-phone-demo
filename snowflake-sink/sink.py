import snowflake.connector
import logging

from quixstreams.sinks import BatchingSink, SinkBatch

logger = logging.getLogger(__name__)

class SnowflakeSink(BatchingSink):
    def __init__(self, warehouse, database, schema, table_name, account, user, password, logger):
        super().__init__()
        self.warehouse = warehouse
        self.database = database
        self.schema = schema
        self.table_name = table_name
        self.account = account
        self.user = user
        self.password = password
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

    def write(self, batch: SinkBatch):
        for item in batch:
            query = f"INSERT INTO {self.table_name} VALUES {item.value}"
            self.cursor.execute(query)
        self.conn.commit()