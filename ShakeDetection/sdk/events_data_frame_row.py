from sdk.quix_data_frame_row import QuixDataFrameRow
import quixstreams as qx

import json

from sdk.stream_data_frame import StreamDataFrame


class EventsDataFrameRow(QuixDataFrameRow):

    def __init__(self, payload: QuixDataFrameRow, parent: StreamDataFrame, stream_id: str, store: qx.LocalFileStorage):
        self.store = store
        event_row = qx.TimeseriesData().add_timestamp_nanoseconds(payload.timestamp.timestamp_nanoseconds)

        for column in payload.parent.columns:
            event_value = payload.timestamp.parameters[column.column_name].string_value
            if event_value is None:
                continue

            event_json = json.loads(event_value)

            flatten_json = self._flatten_data(event_json)

            for inner_column, value in flatten_json.items():
                if len(parent.columns) > 0 and len(list(filter(lambda x: x.column_name == inner_column, parent.columns))) == 0:
                    continue
                event_row = event_row.add_value(inner_column, value)

        self.timestamp = qx.TimeseriesData.from_timestamps([event_row])

        from sdk.quix_data_frame_column import QuixDataFrameColumn
        event_columns = list(map(lambda x: QuixDataFrameColumn(x[0], stream_id, self.store), event_row.parameters.items()))
        parent.columns = parent.columns if len(parent.columns) > 0 else event_columns
        super().__init__(event_row, parent)

    def _flatten_data(self, y):
        out = {}

        def flatten(x, name=''):
            if type(x) is dict:
                for a in x:
                    flatten(x[a], name + a + '_')
            elif type(x) is list:
                i = 0
                for a in x:
                    flatten(a, name + str(i) + '_')
                    i += 1
            else:
                out[name[:-1]] = x

        flatten(y)
        return out