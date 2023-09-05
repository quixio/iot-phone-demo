from __future__ import annotations
from quixstreaming import ParameterData, ParameterDataTimestamp, InputTopic, EventData
from queue import Queue
from threading import Lock
from quixstreaming import StreamReader

from sdk.quix_data_frame_row import QuixDataFrameRow
from sdk.stream_data_frame import StreamDataFrame
from typing import Dict


class SourceDataFrame(StreamDataFrame):
    _checkpoint_mutex = Lock()
    data: Queue[ParameterDataTimestamp] = Queue(5)

    def __init__(self, stream_reader: StreamReader, state: Dict):
        super().__init__(stream_reader, [], None)
        self.stream_reader = stream_reader
        self.state = state
        stream_reader.parameters.on_read += self._on_parameter_data
        stream_reader.events.on_read += self._on_event_data

        for key in self.store.getAllKeys():
            if str(key).startswith("state-" + self.stream_reader.stream_id):
                self.state[key] = self.store.get(key)
                print("State {0} restored.".format(key))

    def _on_event_data(self, data: EventData):
        self._checkpoint_mutex.acquire()

        if len(list(filter(lambda x: x.column_name == data.id, self.columns))) == 0:
            from sdk.quix_data_frame_column import QuixDataFrameColumn
            self.columns.append(QuixDataFrameColumn(data.id, self.stream_reader.stream_id, self.store))

        row = ParameterData().add_timestamp_nanoseconds(data.timestamp_nanoseconds) \
            .add_value(data.id, data.value)

        self.data.put(row, block=True)

        self._checkpoint_mutex.release()

    def _on_parameter_data(self, data: ParameterData):
        self._checkpoint_mutex.acquire()

        for parameter, value in data.timestamps[0].parameters.items():
            if len(list(filter(lambda x: x.column_name == parameter, self.columns))) == 0:
                from sdk.quix_data_frame_column import QuixDataFrameColumn
                self.columns.append(QuixDataFrameColumn(parameter, self.stream_reader.stream_id, self.store))

        for row in data.timestamps:
            self.data.put(row, block=True)

        self._checkpoint_mutex.release()

    async def wait_for_next_item(self):
        while True:
            parent_item = self.data.get(block=True)
            self.data.task_done()
            row = QuixDataFrameRow(parent_item, self)
            return row

    def on_committing(self):

        #print("Commiting started. Queue size " + str(self.data.qsize()))
        self._checkpoint_mutex.acquire()

        self.data.join()

        for key, value in self.state.items():
            self.store.set("state-{0}-{1}".format(self.stream_reader.stream_id, key), value)

        for child in self.children:
            child.on_committing()
        self._checkpoint_mutex.release()
        #print("Committing done. Queue size " + str(self.data.qsize()))
