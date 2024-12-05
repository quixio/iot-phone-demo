import snowflake.connector
import logging

logger = logging.getLogger(__name__)

class SnowflakeSink:
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
        self.cursor = self.conn.cursor()

    def write(self, data):
        try:
            self.cursor.executemany('INSERT INTO {} VALUES (%s, %s, %s)'.format(self.table_name), data)
            self.conn.commit()
        except Exception as e:
            self.logger.error('Failed to insert data into snowflake: {}'.format(e))
            self.conn.rollback()