import snowflake.connector
import logging
from datetime import datetime
import json
from typing_extensions import Optional

from quixstreams.exceptions import QuixException
from quixstreams.sinks import BatchingSink, SinkBatch

__all__ = ("SnowflakeSink", "SnowflakeSinkException")

logger = logging.getLogger(__name__)

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
        table_name: str,
        **kwargs,
    ):
        super().__init__()
        self.database = database
        self.schema = schema
        self.table_name = table_name

        self.conn = snowflake.connector.connect(
            account=account.strip(),
            user=user.strip(),
            password=password.strip(),
            warehouse=warehouse.strip(),
            database=database.strip(),
            schema=schema.strip(),
            timeout=60
        )

        self._init_table()

    def connect(self):
        logger.info(f"Connected to Snowflake DB: {self.database}.{self.schema}.{self.table_name}")

    def _serialize(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        raise TypeError(f"Type {type(obj)} not serializable")

    def write(self, batch: SinkBatch):
        rows = []

        for item in batch:
            row = {k: v for k, v in item.value.items() if v is not None}
            row['timestamp'] = datetime.fromtimestamp(item.timestamp / 1000)
            rows.append(row)

        self._insert_rows(rows)

    def _init_table(self):
        cur = self.conn.cursor()
        cur.execute(f"""
            CREATE TABLE IF NOT EXISTS {self.table_name} (
                "timestamp" TIMESTAMP,
                data VARIANT
            )
        """)
        cur.close()

    def _insert_rows(self, rows):
        cur = self.conn.cursor()
        try:
            for row in rows:
                insert_query = f"INSERT INTO {self.table_name} (timestamp, data) VALUES (%(timestamp)s, PARSE_JSON(%(data)s))"
                cur.execute(insert_query, {
                    'timestamp': row['timestamp'],
                    'data': json.dumps(row, default=self._serialize)
                })
            self.conn.commit()
            logger.debug(f"Inserted {len(rows)} rows into {self.table_name}")
        except snowflake.connector.errors.ProgrammingError as e:
            logger.error(f"Failed to insert rows: {e}")
            raise SnowflakeSinkException(f"Failed to insert rows: {e}")
        finally:
            cur.close()
