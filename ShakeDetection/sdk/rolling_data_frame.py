from typing import Dict

from sdk.rolling_filter import RollingFilter
from enum import  Enum
import pandas as pd
import statistics
import pickle

import quixstreams as qx




class Aggregation(Enum):
    Mean = "mean"

from sdk.stream_data_frame import StreamDataFrame
class RollingDataFrame(StreamDataFrame):
    _rolling_window_data: Dict[int, object]

    def __init__(self, stream_reader: qx.StreamConsumer, columns: [str] = [], rolling_filter: RollingFilter = None,
                 parent_data_frame: StreamDataFrame = None):

        super().__init__(stream_reader, columns, parent_data_frame)

        self._rolling_window_data = dict({})
        self.functions = {}

        self.stream_reader = stream_reader
        self.columns = columns
        self.rolling_filter = rolling_filter
        self.parent_data_frame = parent_data_frame

        self.state_key = "rolling-window-" + self.stream_reader.stream_id

        if self.store.contains_key(self.state_key):
            state_df = pickle.loads(self.store.get(self.state_key))
            state_data = qx.TimeseriesData.from_panda_frame(state_df)

            from sdk.quix_data_frame_row import QuixDataFrameRow
            for row in state_data.timestamps:

                self._rolling_window_data[row.timestamp_milliseconds] = QuixDataFrameRow(row)

            print("State loaded " + str(len(self._rolling_window_data.values())))

    def mean(self):
        for column in self.columns:
            self.functions[column] = Aggregation.Mean

        return self

    def on_committing(self):
        data = qx.TimeseriesData.from_timestamps(list(map(lambda x: x.timestamp, self._rolling_window_data.values())))

        self.store.set(self.state_key, pickle.dumps(data.to_panda_frame()))
        print("State saved.")

    async def wait_for_next_item(self):
        while True:

            row = await self.parent_data_frame.__anext__()
            self._rolling_window_data[row.timestamp.timestamp_milliseconds] = row

            leading_edge_timestamp = max(self._rolling_window_data.keys())
            leading_edge = self._rolling_window_data[leading_edge_timestamp]
            window = pd.Timedelta(self.rolling_filter.window)

            new_window = {}
            for timestamp in self._rolling_window_data.values():
                if timestamp.timestamp.timestamp_milliseconds > leading_edge.timestamp.timestamp_milliseconds - (
                        window.total_seconds() * 1000):
                    new_window[timestamp.timestamp.timestamp_milliseconds] = timestamp

            self._rolling_window_data = new_window

            result = qx.TimeseriesData().add_timestamp_nanoseconds(leading_edge.timestamp.timestamp_nanoseconds)

            for column in self.columns:
                if self.functions[column] is Aggregation.Mean:
                    result.add_value(column, statistics.mean(
                        map(lambda x: x.timestamp.parameters[column].numeric_value, new_window.values())))

            from sdk.quix_data_frame_row import QuixDataFrameRow
            return QuixDataFrameRow(result)

