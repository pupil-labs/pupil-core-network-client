import argparse
import time

import pupil_labs.pupil_core_network_client as pcnc


def main(address: str, port: int):
    device = pcnc.Device(address, port)

    print("Version:", device.request_version())
    print("Start recording:", device.request_recording_start())
    print("Waiting 5 seconds..")
    time.sleep(5.0)
    print("Stop recording:", device.request_recording_stop())


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--address", type=str, default="127.0.0.1")
    parser.add_argument("-p", "--port", type=int, default=50020)
    args = parser.parse_args()

    main(args.address, args.port)
