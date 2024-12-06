import snowflake.connector
import logging

logger = logging.getLogger(__name__)

class SnowflakeSink:
    def __init__(self, warehouse, database, schema, account, user, password, table_name, logger):
        self.warehouse = warehouse
        self.database = database
        self.schema = schema
        self.account = account
        self.user = user
        self.password = password
        self.table_name = table_name
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

    def write(self, data):
        try:
            self.cursor.executemany(f'INSERT INTO {self.table_name} VALUES(%s, %s)', data)
            self.conn.commit()
        except Exception as e:
            self.logger.error(f'Failed to insert data into snowflake: {e}')
            self.conn.rollback()