import argparse
import time

import pupil_labs.pupil_core_network_client as pcnc


def main(address: str, port: int):
    device = pcnc.Device(address, port)

    print(
        "Requesting annotation plugin start...",
        device.request_plugin_start("Annotation_Capture"),
    )
    print("Wait a second for the request to be processed...")
    time.sleep(1.0)

    print(
        "Sending annotation with automatic timestamp",
        device.send_annotation(label="automatic timestamp"),
    )

    print(
        "Sending annotation with custom timestamp",
        # Timestamps should be in Pupil time. By subtracting 5 seconds, the annotation
        # will be associated with a point in time 5 seconds ago.
        device.send_annotation(
            label="custom timestamp", timestamp=device.current_pupil_time() - 5.0
        ),
    )

    print(
        "Sending annotation with custom fields",
        # Custom fields can be passed as keyword arguments and will be saved to their
        # dedicated column during the Pupil Player export
        device.send_annotation(
            label="custom fields", trial=5, subject="me", condition="eye tracking"
        ),
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--address", type=str, default="127.0.0.1")
    parser.add_argument("-p", "--port", type=int, default=50020)
    args = parser.parse_args()

    main(args.address, args.port)
