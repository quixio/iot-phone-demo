from __future__ import annotations
from enum import Enum



class FilterOperation(Enum):
    GE = "ge",
    LE = "le",
    LT = "lt",
    NE = "ne"

class QuixDataFrameRowFilter:

    def __init__(self, column_name: str, filter_value, filter_operation: FilterOperation):
        self.filter_value = filter_value
        self.column_name = column_name
        self.filter_operation = filter_operation

    def evaluate_filter(self, row: QuixDataFrameRow) -> bool:

        if self.filter_operation is FilterOperation.GE:
            value = row[self.column_name]

            return value is not None and value > self.filter_value

        if self.filter_operation is FilterOperation.LE:
            value = row[self.column_name]

            return value is not None and value <= self.filter_value

        if self.filter_operation is FilterOperation.LT:
            value = row[self.column_name]

        if self.filter_operation is FilterOperation.NE:
            value = row[self.column_name]

        return value is not self.filter_value
