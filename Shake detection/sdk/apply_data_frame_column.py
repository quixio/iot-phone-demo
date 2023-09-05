from quixstreaming import LocalFileStorage, ParameterData, ParameterDataTimestamp

from sdk.quix_data_frame_column import QuixDataFrameColumn



class ApplyDataFrameColumn(QuixDataFrameColumn):

    def __init__(self, column_name: str, fn, stream_id: str,  store: LocalFileStorage):
        super().__init__(column_name, stream_id, store)
        self.store = store
        self._fn = fn
        self._stream_id = stream_id
        self.source_column_name = column_name

    def evaluate(self, row: ParameterDataTimestamp):
        parameter = row.parameters[self.source_column_name]
        if parameter.numeric_value is not None:
            new_row_value = parameter.numeric_value
        else:
            new_row_value = parameter.string_value

        return_value = self._fn(new_row_value)

        return return_value



