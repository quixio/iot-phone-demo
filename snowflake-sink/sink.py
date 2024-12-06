import snowflake.connector
from quixstreams.sinks import BatchingSink

class SnowflakeSink(BatchingSink):
    def __init__(self, account, user, password, database, schema, warehouse, table_name, **kwargs):
        super().__init__()
        self.conn_params = {
            'account': account,
            'user': user,
            'password': password,
            'database': database,
            'schema': schema,
            'warehouse': warehouse
        }
        self.table_name = table_name
        self.logger = kwargs.get('logger')

    def connect(self):
        self.connection = snowflake.connector.connect(**self.conn_params)
        self.logger.info(f"Connected to Snowflake with table {self.table_name}")

    def write(self, batch):
        cursor = self.connection.cursor()
        for item in batch:
            columns = ', '.join(item.value.keys())
            values = ', '.join([f'\'{v}\'' if isinstance(v, str) else str(v) for v in item.value.values()])
            sql = f"INSERT INTO {self.table_name} ({columns}) VALUES ({values})"
            try:
                self.logger.debug(sql)
                cursor.execute(sql)
            except Exception as e:
                self.logger.error(f"Failed to insert row: {e}")
        cursor.close()

    def add(self, value, key, timestamp, headers, topic, partition, offset):
        if not isinstance(value, dict):
            raise TypeError(
                f'Sink "{self.__class__.__name__}" supports only dictionaries, got {type(value)}'
            )
        return super().add(
            value=value, key=key, timestamp=timestamp, headers=headers, topic=topic, partition=partition, offset=offset)
