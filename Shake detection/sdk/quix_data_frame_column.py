from quixstreaming import ParameterDataTimestamp, LocalFileStorage

from sdk.quix_data_frame_row_filter import FilterOperation, QuixDataFrameRowFilter


class QuixDataFrameColumn:



    def __init__(self, column_name: str, stream_id: str, store: LocalFileStorage):
        self.column_name = column_name
        self.target_column = ""
        self._stream_id = stream_id
        self._store = store

    def rolling(self, rol: str):
        from sdk.rolling_data_frame import RollingFilter
        from sdk.rolling_data_frame_column import RollingDataFrameColumn
        return RollingDataFrameColumn(self, RollingFilter(rol), self._stream_id, self._store)

    def apply(self, fn):
        from sdk.apply_data_frame_column import ApplyDataFrameColumn
        return ApplyDataFrameColumn(self.column_name, fn, self._stream_id, self._store)

    def evaluate(self, row: ParameterDataTimestamp):
        parameter = row.parameters[self.column_name]
        if parameter.numeric_value is not None:
            return parameter.numeric_value
        else:
            return parameter.string_value

    def on_committing(self):
        return

    def __lt__(self, other):
        return QuixDataFrameRowFilter(self.column_name, other, FilterOperation.LT)

    def __le__(self, other):
        return QuixDataFrameRowFilter(self.column_name, other, FilterOperation.LE)

    def __gt__(self, other):
        return QuixDataFrameRowFilter(self.column_name, other, FilterOperation.GE)

    def __ge__(self, other):
        return (len(self.seq) >= len(other))

    def __eq__(self, other):
        print("eq")
        return (len(self.seq) == len(other))

    def __ne__(self, other):
        print("ne")
        return QuixDataFrameRowFilter(self.column_name, other, FilterOperation.NE)

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return "Column: " + self.column_name