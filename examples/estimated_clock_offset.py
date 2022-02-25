import argparse

import pupil_labs.pupil_core_network_client as pcnc


def main(address: str, port: int):
    device = pcnc.Device(address, port)

    print(
        f"Measured offset between client clock ({device.client_clock}) and pupil "
        f"time:\n\t{device.clock_offset_statistics}"
    )

    print("Current pupil time:", device.current_pupil_time())


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--address", type=str, default="127.0.0.1")
    parser.add_argument("-p", "--port", type=int, default=50020)
    args = parser.parse_args()

    main(args.address, args.port)
