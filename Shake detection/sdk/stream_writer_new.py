from __future__ import annotations

import quixstreams as qx

from sdk.quix_data_frame_row import QuixDataFrameRow

class StreamWriterNew:

    def __init__(self, stream_writer: qx.StreamProducer):

        self._stream_writer = stream_writer

    async def write(self, data):

        if type(data) is QuixDataFrameRow or issubclass(type(data), QuixDataFrameRow):
            print(self._stream_writer)
            row = self._stream_writer.timeseries.buffer.add_timestamp_nanoseconds(data.timestamp.timestamp_nanoseconds)
            for column in data.parent.columns:
                row.add_value(column.column_name, column.evaluate(data.timestamp))

            row.publish()

        from sdk.stream_data_frame import StreamDataFrame
        if type(data) is StreamDataFrame or issubclass(type(data), StreamDataFrame):
            async for row in data:
                self._stream_writer.timeseries.publish(qx.TimeseriesData.from_timestamps([row.timestamp]))
                print("writing row")



