import argparse
import contextlib
import time

import numpy as np

import pupil_labs.pupil_core_network_client as pcnc

current_image = np.zeros((400, 600, 3), dtype=np.uint8)


def main(address: str, port: int, frame_rate_hz: int):
    device = pcnc.Device(address, port)

    source_class_name = "HMD_Streaming_Source"
    frame_topic = "hmd_streaming.custom"
    device.request_plugin_start(source_class_name, args={"topics": (frame_topic,)})
    for eye_id in range(2):
        device.request_plugin_start_eye_process(
            eye_id, source_class_name, args={"topics": (frame_topic,)}
        )

    with contextlib.suppress(KeyboardInterrupt):
        increasing_index = 0
        while True:
            send_image(
                device,
                gray_image(increasing_index),
                frame_topic,
                increasing_index,
                timestamp=device.current_pupil_time(),
            )
            increasing_index += 1
            time.sleep(1 / frame_rate_hz)


def send_image(device: pcnc.Device, image, topic: str, index: int, timestamp: float):
    height, width, depth = image.shape
    device.send_message(
        {
            "format": "bgr",
            "projection_matrix": [  # dummy pin-hole camera intrinsics
                [1000, 0.0, width / 2.0],
                [0.0, 1000, height / 2.0],
                [0.0, 0.0, 1.0],
            ],
            "topic": topic,
            "width": width,
            "height": height,
            "index": index,
            "timestamp": timestamp,
            "__raw_data__": [image],
        }
    )


def gray_image(color_seed: int):
    """Return an image with a gray value between 85 and 170"""
    return current_image + (color_seed % 85) + 85


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--address", type=str, default="127.0.0.1")
    parser.add_argument("-p", "--port", type=int, default=50020)
    parser.add_argument("-fps", "--frame-rate", type=int, default=60)
    args = parser.parse_args()

    main(args.address, args.port, args.frame_rate)
