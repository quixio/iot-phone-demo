import snowflake.connector
from quixstreams.sinks import BatchingSink, SinkBatch


class SnowflakeSink(BatchingSink):
    def __init__(
        self,
        account,
        warehouse,
        database,
        schema,
        table_name,
        user,
        password
    ):
        super().__init__()
        self.account = account
        self.warehouse = warehouse
        self.database = database
        self.schema = schema
        self.table_name = table_name
        self.user = user
        self.password = password

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
            self.cursor.execute(
                "INSERT INTO {} (KEY, VALUE, TIMESTAMP) VALUES (%s, %s, %s)".format(self.table_name),
                (item.key, item.value, item.timestamp)
            )
        self.conn.commit()