from sdk.events_data_frame_row import EventsDataFrameRow
import quixstreams as qx

from sdk.stream_data_frame import StreamDataFrame
import time


class EventsDataFrame(StreamDataFrame):

    def __init__(self, stream_reader: qx.StreamConsumer, columns, parent_data_frame: StreamDataFrame, store: qx.LocalFileStorage):
        super().__init__(stream_reader, columns, parent_data_frame)
        self.store = store
        self.source_columns = columns
        self.columns = []

    async def wait_for_next_item(self):
        row = await self.parent_data_frame.__anext__()

        events_row = EventsDataFrameRow(row, self, self.stream_reader.stream_id,  self.store)



        return events_row
