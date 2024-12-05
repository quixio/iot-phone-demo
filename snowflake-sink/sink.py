import snowflake.connector

class SnowflakeSink:
    def __init__(self, user, password, account, warehouse, database, schema, table):
        self.user = user
        self.password = password
        self.account = account
        self.warehouse = warehouse
        self.database = database
        self.schema = schema
        self.table = table

    def connect(self):
        self.conn = snowflake.connector.connect(user=self.user, password=self.password, account=self.account)
        self.conn.cursor().execute(f'USE WAREHOUSE {self.warehouse}')
        self.conn.cursor().execute(f'USE DATABASE {self.database}')
        self.conn.cursor().execute(f'USE SCHEMA {self.schema}')

    def write(self, data):
        cursor = self.conn.cursor()
        cursor.execute(f'INSERT INTO {self.table} VALUES (%s)', (data,))