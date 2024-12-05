import snowflake.connector

from quixstreams.sinks import Sink


class SnowflakeSink(Sink):
    def __init__(self, warehouse, database, schema, table_name, account, user, password, logger):
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

    def write(self, batch):
        cursor = self.conn.cursor()
        for item in batch:
            cursor.execute(
                f"INSERT INTO {self.table_name} VALUES (%s, %s, %s)",
                (item.key, item.value, item.timestamp)
            )