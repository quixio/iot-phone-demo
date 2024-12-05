import json
import logging
import snowflake.connector
from snowflake.connector import connect, DictCursor
from quixstreams.sinks import BatchingSink
from quixstreams.models import HeaderValue
from typing import Any

class SnowflakeSink(BatchingSink):

    def __init__(self, account, user, password, warehouse, database, schema, table, role=None):
        self.table = table
        self.schema = schema
        self.database = database

        self.conn = snowflake.connector.connect(
            user=user,
            password=password,
            account=account,
            warehouse=warehouse,
            database=database,
            schema=schema,
            role=role
        )

    def close(self):
        self.conn.close()

    def write(self, batch):
        cursor = self.conn.cursor(DictCursor)

        for item in batch:

            cols = ",".join(item.value.keys())
            vals = [json.dumps(v) if isinstance(v, dict) else v for v in item.value.values()]
            vals = list(map(lambda x: str(x) if x is not None else 'NULL', vals))
            sql = "INSERT INTO {} ({}) VALUES ({})".format(self.table, cols, ",".join(['%s'] * len(vals)))
            cursor.execute(sql, tuple(vals))

        self.conn.commit()
        cursor.close()

    def add(
        self,
        value: Any,
        key: Any,
        timestamp: int,
        headers: list[tuple[str, HeaderValue]],
        topic: str,
        partition: int,
        offset: int
    ):
        return super().add(
            value=value,
            key=key,
            timestamp=timestamp,
            headers=headers,
            topic=topic,
            partition=partition,
            offset=offset
        )