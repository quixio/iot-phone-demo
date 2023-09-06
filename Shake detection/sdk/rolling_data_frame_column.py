import pickle
import quixstreams as qx


from sdk.quix_data_frame_column import QuixDataFrameColumn
from sdk.rolling_data_frame import RollingFilter, Aggregation
import pandas as pd
import statistics


class RollingDataFrameColumn(QuixDataFrameColumn):

    def __init__(self, source_column: QuixDataFrameColumn, rolling_filter: RollingFilter, stream_id: str,  store: qx.LocalFileStorage):
        super().__init__(source_column.column_name, stream_id, store)
        self.store = store
        self._rolling_window_data = {}
        self._stream_id = stream_id
        self.rolling_filter = rolling_filter
        self.source_column = source_column

        self.aggregation = Aggregation.Mean

        self.state_key = "rolling-window-{0}-{1}".format(self.column_name, self._stream_id)

        if self.store.contains_key(self.state_key):
            state_values = pickle.loads(self.store.get(self.state_key))
            self._rolling_window_data = state_values

            print("State loaded " + str(len(self._rolling_window_data.values())))

    def mean(self):
        self.aggregation = Aggregation.Mean
        return self

    def on_committing(self):
        self.store.set(self.state_key, pickle.dumps(self._rolling_window_data))

    def evaluate(self, row: qx.TimeseriesDataTimestamp):
        new_row_value = self.source_column.evaluate(row)

        self._rolling_window_data[row.timestamp_milliseconds] = new_row_value

        leading_edge_timestamp = max(self._rolling_window_data.keys())
        window = pd.Timedelta(self.rolling_filter.window)

        new_window = {}
        for timestamp, value in self._rolling_window_data.items():
            if timestamp > (leading_edge_timestamp - (window.total_seconds() * 1000)):
                new_window[timestamp] = value

        self._rolling_window_data = new_window

        return statistics.mean(map(lambda x: x, new_window.values()))



