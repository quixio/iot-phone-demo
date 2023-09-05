from quixstreaming import ParameterDataTimestamp

from sdk.stream_data_frame import StreamDataFrame
import pandas as pd

class StreamDataFrameRowSelection:

    def __init__(self, columns:[str], timestamp: ParameterDataTimestamp, parent: StreamDataFrame):
        self.timestamp = timestamp
        self.parent = parent
        self.columns = columns

    def __getitem__(self, key):

        if key == "timestamp":
            return self.timestamp.timestamp

        columns_filtered = list(filter(lambda x: x.column_name == key, self.parent.columns))

        if len(columns_filtered) == 0:
            return None
        else:
            return columns_filtered[0].evaluate(self.timestamp)

    def __setitem__(self, key, value):
        self.__setattr__(key, value)

    def __str__(self):
        result = "|"

        result = result + str(self.timestamp.timestamp)[:self.parent.get_columns_print_width()] + self.padding[
                                                                                                  :max(0,
                                                                                                       self.parent.get_columns_print_width() - len(
                                                                                                           str(self.timestamp.timestamp)))] + "|"

        for column_key in self.columns:
            column = filter(lambda x: x.column_name == column_key, self.parent.columns)[0]
            value = str(column.evaluate(self.timestamp))[:self.parent.get_columns_print_width()]
            result = result + self.padding[
                              :max(self.parent.get_columns_print_width() - len(value), 0)] + value + "|"

        return result

    def to_pandas_series(self):

        row_data = []
        for column_key in self.columns:
            column = list(filter(lambda x: x.column_name == column_key, self.parent.columns))[0]

            row_data.append(column.evaluate(self.timestamp))

        return pd.DataFrame(
            data=[row_data],
            columns=self.columns
        )