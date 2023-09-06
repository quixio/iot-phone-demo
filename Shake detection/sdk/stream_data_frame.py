from __future__ import annotations
import quixstreams as qx

from queue import Queue
from sdk.quix_data_frame_row_filter import QuixDataFrameRowFilter
from sdk.quix_data_frame_column import QuixDataFrameColumn


class StreamDataFrameHeader:

    padding = "                              "
    border = "------------------------------"


    def __init__(self, columns: [QuixDataFrameColumn], columns_print_width: int):
        self.columns = columns
        self.columns_print_width = columns_print_width



    def __str__(self):
        result = "|"

        result = result + "Timestamp" + self.padding[:self.columns_print_width-9] + "|"

        for column in self.columns:
            result = result + column.column_name[:self.columns_print_width] + self.padding[:max(self.columns_print_width-len(column.column_name), 0)] + "|"

        result = result + "\n|"
        result = result + self.border[:self.columns_print_width] + "|"

        for column in self.columns:
            result = result + self.border[:self.columns_print_width] + "|"

        return result

class StreamDataFrame:
    _data: Queue[ParameterDataTimestamp]
    children : [StreamDataFrame]

    columns: []
    columns_print_width = 30


    def __init__(self, stream_reader: qx.StreamConsumer, columns: [QuixDataFrameColumn] = [], parent_data_frame: StreamDataFrame = None):
        self.stream_reader = stream_reader
        self.columns = columns
        self.parent_data_frame = parent_data_frame
        self.store = qx.LocalFileStorage()
        self.children = []
        self._data = Queue(5)
        self.state = {}

    def get_columns_print_width(self):
        if self.parent_data_frame is None:
            return self.columns_print_width
        else:
            return self.parent_data_frame.get_columns_print_width()

    def set_columns_print_width(self, width):
        if self.parent_data_frame is None:
            self.columns_print_width = width
        else:
            self.parent_data_frame.set_columns_print_width(width)


    def get_header(self) -> StreamDataFrameHeader:
        return StreamDataFrameHeader(self.columns, self.get_columns_print_width())

    header = property(get_header)

    def rolling(self, window: str):
        from sdk.rolling_data_frame import RollingDataFrame, RollingFilter
        rdf = RollingDataFrame(self.stream_reader, self.columns, RollingFilter(window), self)
        self.children.append(rdf)
        return rdf

    def apply(self, fn):
        from sdk.apply_data_frame import ApplyDataFrame
        column = ApplyDataFrame(self, fn, self.stream_reader.stream_id, self.store)
        return column

    def flatten_json_events(self):
        from sdk.events_data_frame import EventsDataFrame
        events_data_frame = EventsDataFrame(self.stream_reader, self.columns, self, self.store)
        self.children.append(events_data_frame)

        return events_data_frame

    def __iter__(self):
        return self

    def __next__(self):  # Python 2: def next(self)
        self._data.get(block=True)

    def __aiter__(self):
        return self

    async def wait_for_next_item(self):
        while True:
            row = await self.parent_data_frame.__anext__()

            row.parent = self
            return row

    async def __anext__(self):
        item = await self.wait_for_next_item()

        return item

    def on_committing(self):

        for column in self.columns:
            column.on_committing()

        for child in self.children:
            child.on_committing()

    def __setitem__(self, key, value):
        value.column_name = key
        self.columns.append(value)

    def __getitem__(self, key) -> QuixDataFrameColumn | StreamDataFrame:
        print(type(key))
        print(key)
        if type(key) is str:
            return list(filter(lambda x: x.column_name == key, self.columns))[0]
        if type(key) is QuixDataFrameRowFilter:
            from sdk.filter_data_frame import FilterDataFrame
            df = FilterDataFrame(self.stream_reader, self.columns, key, self)
            self.children.append(df)

            return df
        if type(key) is list:
            from sdk.quix_data_frame_column import QuixDataFrameColumn
            selected_columns = list(map(lambda x: QuixDataFrameColumn(x, self.stream_reader.stream_id, self.store), key))

            df = StreamDataFrame(self.stream_reader, selected_columns, self)
            self.children.append(df)

            return df



