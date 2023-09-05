from quixstreaming import ParameterDataTimestamp

from sdk.stream_data_frame import StreamDataFrame


class QuixDataFrameRow:

    padding = "                              "


    def __init__(self, timestamp: ParameterDataTimestamp, parent: StreamDataFrame):
        self.timestamp = timestamp
        self.parent = parent

    def __getitem__(self, key):

        if type(key) is list:
            from sdk.stream_data_frame_row_selection import StreamDataFrameRowSelection
            return StreamDataFrameRowSelection(key, self.timestamp, self.parent)

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

        result = result + str(self.timestamp.timestamp)[:self.parent.get_columns_print_width()] + self.padding[:max(0, self.parent.get_columns_print_width() - len(str(self.timestamp.timestamp)) )] + "|"

        for column in self.parent.columns:
            value = str(column.evaluate(self.timestamp))[:self.parent.get_columns_print_width()]
            result = result + self.padding[:max(self.parent.get_columns_print_width() - len(value), 0)] + value +  "|"

        return result
