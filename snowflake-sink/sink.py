import logging
import time
from typing import Any, Mapping

from quixstreams.exceptions import QuixException
from quixstreams.models import HeadersTuples
from quixstreams.sinks import BatchingSink, SinkBatch

import snowflake.connector

__all__ = ("SnowflakeSink", "SnowflakeSinkException")

logger = logging.getLogger(__name__)

_KEY_COLUMN_NAME = "__key"
_TIMESTAMP_COLUMN_NAME = "timestamp"

class SnowflakeSinkException(QuixException): pass

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
        """
        A connector to sink processed data to Snowflake.

        It batches the processed records in memory per topic partition, and flushes them to Snowflake at the checkpoint.

        >***NOTE***: SnowflakeSink can accept only dictionaries.
        > If the record values are not dicts, you need to convert them to dicts before
        > sinking.

        :param account: Snowflake account identifier.
        :param user: Snowflake user.
        :param password: Snowflake user password.
        :param database: Snowflake database name.
        :param schema: Snowflake schema name.
        :param warehouse: Snowflake warehouse name.
        :param table_name: Snowflake table name.
        :param kwargs: Additional keyword arguments for the Snowflake connector.
        """

        super().__init__()
        self.connection = snowflake.connector.connect(
            account=account,
            user=user,
            password=password,
            database=database,
            schema=schema,
            warehouse=warehouse,
            **kwargs
        )
        self.table_name = table_name
        self._ensure_table_exists()

    def _ensure_table_exists(self):
        """Checks if table exists in Snowflake, creates it if not."""
        cursor = self.connection.cursor()
        try:
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {self.table_name} (
                    "{_KEY_COLUMN_NAME}" STRING,
                    "{_TIMESTAMP_COLUMN_NAME}" TIMESTAMP,
                    data VARIANT
                )
            """)
        finally:
            cursor.close()

    def write(self, batch: SinkBatch):
        rows = []
        for item in batch:
            row = {"data": item.value}  # Storing complete JSON as VARIANT
            # Add key and timestamp values
            if item.key is not None:
                row[_KEY_COLUMN_NAME] = item.key
            row[_TIMESTAMP_COLUMN_NAME] = item.timestamp  # Snowflake can accept epoch time directly
            rows.append(row)

        cursor = self.connection.cursor()
        try:
            insert_cmd = f"INSERT INTO {self.table_name} ({_KEY_COLUMN_NAME}, {_TIMESTAMP_COLUMN_NAME}, data) VALUES (%(__key)s, %(timestamp)s, parse_json(%(data)s))"
            cursor.executemany(insert_cmd, rows)
        finally:
            cursor.close()

    def add(
        self,
        value: Any,
        key: Any,
        timestamp: int,
        headers: HeadersTuples,
        topic: str,
        partition: int,
        offset: int,
    ):
        if not isinstance(value, Mapping):
            raise TypeError(
                f'Sink "{self.__class__.__name__}" supports only dictionaries,'
                f" got {type(value)}"
            )
        return super().add(
            value=value,
            key=key,
            timestamp=timestamp,
            headers=headers,
            topic=topic,
            partition=partition,
            offset=offset,
        )
