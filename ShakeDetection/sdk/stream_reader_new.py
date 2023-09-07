from __future__ import annotations
import asyncio
import quixstreams as qx

from threading import Thread


from sdk.stream_writer_new import StreamWriterNew
from sdk.source_data_frame import SourceDataFrame


class StreamReaderNew:
    stream_tasks = []

    _df: StreamReaderNew

    def __init__(self, input_topic: qx.TopicConsumer, stream_reader: qx.StreamConsumer, stream_writer: qx.StreamProducer):
        self._stream_reader = stream_reader
        self._stream_writer = stream_writer
        self.input_topic = input_topic
        self._df = None
        self.state = {}

        input_topic.on_committing = self.on_committing

    def on_committing(self, topic_consumer):
        if self._df is not None:
            self._df.on_committing()

    def _get_stream_id(self):
        return self._stream_reader.stream_id

    stream_id = property(_get_stream_id)

    def get_df(self) -> SourceDataFrame:
        from sdk.source_data_frame import SourceDataFrame
        self._df = SourceDataFrame(self._stream_reader, self.state)

        return self._df

    df = property(get_df)

    @classmethod
    def process_stream(cls, input_topic: qx.TopicConsumer, output_topic: qx.TopicProducer, fn):

        def _on_new_stream(input_stream: qx.StreamConsumer):

            stream_writer = output_topic.get_or_create_stream(input_stream.stream_id)
            stream_reader = StreamReaderNew(input_topic, input_stream, stream_writer)

            stream_writer_wrapper = StreamWriterNew(stream_writer)

            def create_stream_thread():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                task = fn(stream_reader, stream_writer_wrapper)
                loop.run_until_complete(task)

            t = Thread(target=create_stream_thread, args=[])
            t.start()

        input_topic.on_stream_received = _on_new_stream

    def __delitem__(self, key):
        self.__delattr__(key)

    def __getitem__(self, key):
        return self.__getattribute__(key)

    def __setitem__(self, key, value):
        self.__setattr__(key, value)
