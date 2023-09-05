from sdk.quix_data_frame_row_filter import QuixDataFrameRowFilter
from sdk.stream_data_frame import StreamDataFrame
from quixstreaming import StreamReader


class FilterDataFrame(StreamDataFrame):

    def __init__(self, stream_reader: StreamReader, columns: [str] = [], row_filter: QuixDataFrameRowFilter = None,
                 parent_data_frame: StreamDataFrame = None):

        super().__init__(stream_reader, columns, parent_data_frame)

        self.stream_reader = stream_reader
        self.columns = columns
        self.row_filter = row_filter
        self.parent_data_frame = parent_data_frame

    async def wait_for_next_item(self):
        while True:
            row = await self.parent_data_frame.__anext__()
            if self.row_filter is None or self.row_filter.evaluate_filter(row):
                row.parent = self
                return row