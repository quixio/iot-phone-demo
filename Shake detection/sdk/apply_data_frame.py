import quixstreams as qx
from sdk.quix_data_frame_column import QuixDataFrameColumn
from sdk.quix_data_frame_row import QuixDataFrameRow
from sdk.stream_data_frame import StreamDataFrame


class ApplyDataFrame(QuixDataFrameColumn):

    def __init__(self, parent_frame: StreamDataFrame, fn, stream_id: str,  store: qx.LocalFileStorage):
        super().__init__("", stream_id, store)
        self.store = store
        self._fn = fn
        self._stream_id = stream_id
        self._parent_frame= parent_frame

    def evaluate(self, row: qx.ParameterDataTimestamp):

        return_value = self._fn(QuixDataFrameRow(row, self._parent_frame))

        return return_value