import argparse
import contextlib
import logging
import time

import pupil_labs.pupil_core_network_client as pcnc


def main(address: str, port: int, max_frame_rate_hz: int):
    device = pcnc.Device(address, port)
    device.send_notification(
        {"subject": "frame_publishing.set_format", "format": "bgr"}
    )

    with contextlib.suppress(KeyboardInterrupt):
        with device.subscribe_in_background("frame.world", buffer_size=1) as sub:
            while True:
                message = sub.recv_new_message()
                print(
                    f"[{message.payload['timestamp']}] {message.payload['topic']} "
                    f"{message.payload['index']}"
                )
                time.sleep(1 / max_frame_rate_hz)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--address", type=str, default="127.0.0.1")
    parser.add_argument("-p", "--port", type=int, default=50020)
    parser.add_argument("-fps", "--max-frame-rate", type=int, default=10)
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()
    logging.basicConfig(level=logging.DEBUG if args.debug else logging.WARNING)

    main(args.address, args.port, args.max_frame_rate)
