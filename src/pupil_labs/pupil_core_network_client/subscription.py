from __future__ import annotations

import logging
import threading
from collections import deque
from typing import ByteString, Deque, NamedTuple, Sequence

import msgpack
import zmq

from .decorators import ensure_connected

logger = logging.getLogger(__name__)


class Message(NamedTuple):
    topic: str
    "Message topic"
    payload: dict
    "Message payload"

    @property
    def raw_data(self) -> Sequence[ByteString] | None:
        return self.payload.get("__raw_data__")


class Subscription:
    def __init__(
        self,
        address: str = "127.0.0.1",
        *,
        port: int,
        topics: str | Sequence[str],
    ) -> None:
        self.address = address
        self.port = port
        self.topics: tuple[str] = (
            (topics,) if isinstance(topics, str) else tuple(topics)
        )
        self._sub_socket = None
        self.connect()

    @property
    def is_connected(self):
        return self._sub_socket is not None

    def connect(self):
        if self.is_connected:
            self.disconnect()
        self._sub_socket = zmq.Context.instance().socket(zmq.SUB)
        url = f"tcp://{self.address}:{self.port}"
        logger.debug(f"Connecting to {url}")
        self._sub_socket.connect(url)
        for topic in self.topics:
            logger.debug(f"Subscribing to {topic}...")
            self._sub_socket.subscribe(topic)

    def disconnect(self):
        if self._sub_socket:
            self._sub_socket.close()
            self._sub_socket = None

    @property
    @ensure_connected
    def has_new_message(self) -> bool:
        return self._sub_socket.get(zmq.EVENTS) & zmq.POLLIN

    @ensure_connected
    def recv_new_message(self, timeout_ms: int | None = None) -> Message | None:
        """Recv a message with topic, payload.
        Topic is a utf-8 encoded string. Returned as unicode object.
        Payload is a msgpack serialized dict. Returned as a python dict.
        Any addional message frames will be added as a list
        in the payload dict with key: '__raw_data__' .
        """
        if self._sub_socket.poll(timeout_ms):
            topic = self._recv_topic()
            remaining_frames = self._recv_remaining_frames()
            payload = self._deserialize_payload(*remaining_frames)
            return Message(topic, payload)
        else:
            return None

    def _recv_topic(self):
        return self._sub_socket.recv_string()

    def _recv_remaining_frames(self):
        while self._sub_socket.get(zmq.RCVMORE):
            yield self._sub_socket.recv()

    def _deserialize_payload(
        self, payload_serialized: ByteString, *extra_frames
    ) -> dict:
        payload = msgpack.unpackb(payload_serialized)
        if extra_frames:
            payload["__raw_data__"] = extra_frames
        return payload

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        self.disconnect()


class BackgroundSubscription(Subscription):
    """Process subscription in background and buffer recent messages"""

    def __init__(self, *args, buffer_size: int | None, **kwargs) -> None:
        self._queue: Deque[Message] = deque(maxlen=buffer_size)
        self._new_item_event = threading.Event()
        self._is_connected_flag = threading.Event()
        self._worker_thread = None
        super().__init__(*args, **kwargs)

    @property
    def is_connected(self):
        return self._is_connected_flag.is_set()

    def connect(self):
        self._worker_thread = threading.Thread(target=self._buffer_messages)
        self._worker_thread.start()
        self._is_connected_flag.wait()

    def disconnect(self):
        self._is_connected_flag.clear()
        self._worker_thread.join()
        self._worker_thread = None

    @property
    @ensure_connected
    def has_new_message(self) -> bool:
        return bool(self._queue)

    @ensure_connected
    def recv_new_message(self, timeout_ms: int | None = None) -> Message:
        try:
            return self._queue.popleft()
        except IndexError:
            self._new_item_event.clear()
            timeout_s = (timeout_ms / 1000) if timeout_ms else timeout_ms
            if self._new_item_event.wait(timeout=timeout_s):
                return self._queue.popleft()

    def _buffer_messages(self):
        with Subscription(self.address, port=self.port, topics=self.topics) as sub:
            self._is_connected_flag.set()
            while self._is_connected_flag.is_set():
                message = sub.recv_new_message(timeout_ms=250)
                if message:
                    self._queue.append(message)
                    self._new_item_event.set()
