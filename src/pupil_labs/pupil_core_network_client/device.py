from __future__ import annotations

import logging
import statistics
import time
from typing import Callable, NamedTuple, Sequence, TypeVar

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal

import msgpack
import zmq

from . import __version__
from .decorators import ensure_connected
from .subscription import BackgroundSubscription, Subscription

ClockFunction = Callable[[], float]
T = TypeVar('T')


logger = logging.getLogger(__name__)


class Device:
    def __init__(
        self,
        address: str = "127.0.0.1",
        port: int = 50020,
        client_clock: ClockFunction = time.monotonic,
    ) -> None:
        self.client_clock: ClockFunction = client_clock
        "Client clock function. Returns time in seconds."
        self.address = address
        self.port = port
        self.clock_offset_statistics: ClockOffsetStatistics = None
        "Statistic results of the clock offset estimation"
        self._req_socket = None
        self.connect()

    @property
    def is_connected(self):
        return self._req_socket is not None

    def connect(self):
        if self.is_connected:
            self.disconnect()
        self._req_socket = zmq.Context.instance().socket(zmq.REQ)
        self._req_socket.connect(f"tcp://{self.address}:{self.port}")
        self._announce(f"connected.v{__version__}")
        self._update_ipc_backend_ports()
        self.estimate_client_to_remote_clock_offset()

    def disconnect(self):
        if self._req_socket:
            self._req_socket.close()
            self._req_socket = None

    @ensure_connected
    def current_pupil_time(self) -> float:
        return self.client_clock() + self.clock_offset_statistics.mean_offset

    @ensure_connected
    def request_current_pupil_time(self) -> float:
        return self._send_recv_command("t", type_=float)

    @ensure_connected
    def request_version(self) -> str:
        return self._send_recv_command("v")

    @ensure_connected
    def request_recording_start(self, session_name: str | None = None) -> str:
        cmd = f"R {session_name}" if session_name else "R"
        return self._send_recv_command(cmd)

    @ensure_connected
    def request_recording_stop(self) -> str:
        return self._send_recv_command("r")

    @ensure_connected
    def request_calibration_start(self) -> str:
        return self._send_recv_command("C")

    @ensure_connected
    def request_calibration_stop(self) -> str:
        return self._send_recv_command("c")

    @ensure_connected
    def request_plugin_start(
        self, plugin_class_name: str, args: dict | None = None
    ) -> str:
        notification = {"subject": "start_plugin", "name": plugin_class_name}
        if args is not None:
            notification["args"] = args
        return self.send_notification(notification)

    @ensure_connected
    def request_plugin_start_eye_process(
        self, eye_id: Literal[0, 1], plugin_class_name: str, args: dict | None = None
    ) -> str:
        if eye_id not in (0, 1):
            raise ValueError(f"Unexpected `eye_id`: {eye_id}")
        notification = {
            "subject": "start_eye_plugin",
            "target": f"eye{eye_id}",
            "name": plugin_class_name,
        }
        if args is not None:
            notification["args"] = args
        return self.send_notification(notification)

    @ensure_connected
    def send_notification(self, notification: dict) -> str:
        """Sends ``notification`` to Pupil Remote"""
        if "subject" not in notification:
            raise ValueError("`notification` requires a subject field")

        prefix = "notify."
        topic_key = "topic"
        if topic_key in notification and not notification[topic_key].startswith(prefix):
            raise ValueError(
                "`notification` contains `topic` field but it does not have the "
                "necessary prefix `notify.`"
            )
        if topic_key not in notification:
            notification[topic_key] = prefix + notification["subject"]
        return self.send_message(notification)

    @ensure_connected
    def send_annotation(
        self, label: str, timestamp: float | None = None, **kwargs
    ) -> str:
        if timestamp is None:
            timestamp = self.current_pupil_time()
        return self.send_message(
            {"topic": "annotation", "label": label, "timestamp": timestamp, **kwargs}
        )

    @ensure_connected
    def send_message(self, payload: dict) -> str:
        if "topic" not in payload:
            raise ValueError("`payload` needs to contain `topic` field")
        if "__raw_data__" not in payload:
            # IMPORTANT: serialize first! Else if there is an exception
            # the next message will have an extra prepended frame
            serialized_payload = msgpack.packb(payload, use_bin_type=True)
            self._req_socket.send_string(payload["topic"], flags=zmq.SNDMORE)
            self._req_socket.send(serialized_payload)
        else:
            extra_frames = payload.pop("__raw_data__")
            if not isinstance(extra_frames, Sequence):
                raise ValueError("`payload['__raw_data__'] needs to be a sequence`")
            self._req_socket.send_string(payload["topic"], flags=zmq.SNDMORE)
            serialized_payload = msgpack.packb(payload, use_bin_type=True)
            self._req_socket.send(serialized_payload, flags=zmq.SNDMORE)
            for frame in extra_frames[:-1]:
                self._req_socket.send(frame, flags=zmq.SNDMORE, copy=True)
            self._req_socket.send(extra_frames[-1], copy=True)
        return self._req_socket.recv_string()

    @ensure_connected
    def estimate_client_to_remote_clock_offset(
        self, num_measurements: int = 10
    ) -> ClockOffsetStatistics:
        """Returns the clock offset after multiple measurements to reduce the effect
        of varying network delay.

        Since the network connection to Pupil Capture/Service is not necessarily stable,
        one has to assume that the delays to send and receive commands are not
        symmetrical and might vary. To reduce the possible clock-offset estimation
        error, this function repeats the measurement multiple times and returns the mean
        clock offset. The variance of these measurements is expected to be higher for
        remote connections (two different computers) than for local connections (script
        and Core software running on the same computer). You can easily extend this
        function to perform further statistical analysis on your clock-offset
        measurements to examine the accuracy of the time sync.

        Description taken and code adopted from `pupil helpers remote_annotations.py
        <https://github.com/pupil-labs/pupil-helpers/blob/6e2cd2fc28c8aa954bfba068441dfb582846f773/python/remote_annotations.py#L161>`__
        """
        self._announce(f"clock_offset_estimation.x{num_measurements}")
        if num_measurements < 2:
            raise ValueError("Needs to perform at least two measurement")

        offsets = [
            self.measure_one_client_to_remote_clock_offset()
            for x in range(num_measurements)
        ]
        self.clock_offset_statistics = ClockOffsetStatistics(
            statistics.mean(offsets), statistics.stdev(offsets), num_measurements
        )
        return self.clock_offset_statistics

    @ensure_connected
    def measure_one_client_to_remote_clock_offset(self):
        """Calculates the offset between the Pupil Core software clock and a local clock

        Requesting the remote pupil time takes time. This delay needs to be considered
        when calculating the clock offset. We measure the local time before (A) and
        after (B) the request and assume that the remote pupil time was measured at
        (A+B)/2, i.e. the midpoint between A and B.
        As a result, we have two measurements from two different clocks that were taken
        assumingly at the same point in time. The difference between them ("clock
        offset") allows us, given a new local clock measurement, to infer the
        corresponding time on the remote clock.

        Description taken and code adopted from `pupil helpers remote_annotations.py
        <https://github.com/pupil-labs/pupil-helpers/blob/6e2cd2fc28c8aa954bfba068441dfb582846f773/python/remote_annotations.py#L161>`__
        """
        local_time_before = self.client_clock()
        pupil_time = self.request_current_pupil_time()
        local_time_after = self.client_clock()

        local_time = (local_time_before + local_time_after) / 2.0
        clock_offset = pupil_time - local_time
        return clock_offset

    @ensure_connected
    def subscribe(self, topics: str | Sequence[str]) -> Subscription:
        self._announce(f"subscription.{topics}")
        return Subscription(self.address, port=self.ipc_sub_port, topics=topics)

    @ensure_connected
    def subscribe_in_background(
        self, topics: str | Sequence[str], buffer_size: int | None = None
    ) -> Subscription:
        self._announce(f"subscription.{topics}")
        return BackgroundSubscription(
            self.address, port=self.ipc_sub_port, topics=topics, buffer_size=buffer_size
        )

    def _announce(self, announcement: str):
        prefix = "pupil_labs.pupil_core_network_client."
        self.send_notification({"subject": prefix + announcement})

    def _update_ipc_backend_ports(self):
        self.ipc_pub_port = int(self._send_recv_command("PUB_PORT"))
        self.ipc_sub_port = int(self._send_recv_command("SUB_PORT"))

    def _send_recv_command(self, cmd: str, type_: type[T] = str) -> T:
        self._req_socket.send_string(cmd)
        return type_(self._req_socket.recv_string())


class ClockOffsetStatistics(NamedTuple):
    mean_offset: float
    "Clock offset mean, in seconds"
    std_offset: float
    "Clock offset standard deviation, in seconds"
    num_measurements: int
    "Number of measurements (at least 2)"
