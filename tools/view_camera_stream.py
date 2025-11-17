#!/usr/bin/env python3
"""
Simple viewer for the Unitree Isaac Lab camera stream.

The simulation publishes concatenated JPEG frames over ZeroMQ (PUB) at tcp://<host>:<port>.
Each frame contains the head, left wrist, and right wrist camera views stitched horizontally.
This script subscribes to that stream, decodes the images, and optionally shows the split views.
"""
import argparse
import sys
from typing import List

import cv2
import numpy as np
import zmq


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="View Isaac Lab streamed camera images.")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host/IP running sim_main ImageServer.")
    parser.add_argument("--port", type=int, default=5555, help="ZeroMQ port (match IMAGE_SERVER_PORT if set).")
    parser.add_argument(
        "--show-split",
        action="store_true",
        help="Display individual head/left/right windows in addition to the concatenated image.",
    )
    parser.add_argument(
        "--window-prefix",
        type=str,
        default="IsaacCam",
        help="Prefix for OpenCV windows (useful when running multiple viewers).",
    )
    parser.add_argument(
        "--views",
        nargs="+",
        default=["head", "cam_left_high", "cam_right_high", "left", "right"],
        help="Ordered list of view names to split and display (must match writer order).",
    )
    return parser.parse_args()


def split_views(image: np.ndarray, view_names: List[str]) -> List[np.ndarray]:
    """Split a horizontally concatenated image into equally sized views."""
    if image is None or image.size == 0:
        return []

    num_views = len(view_names)
    width = image.shape[1]
    single_width = width // num_views if num_views > 0 else width

    views = []
    for idx in range(num_views):
        start = idx * single_width
        end = start + single_width
        views.append(image[:, start:end])
    return views


def main() -> int:
    args = parse_args()

    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.setsockopt(zmq.SUBSCRIBE, b"")
    socket.setsockopt(zmq.RCVHWM, 1)  # Drop old frames if GUI is slow.

    endpoint = f"tcp://{args.host}:{args.port}"
    print(f"[viewer] Connecting to {endpoint} ...")
    socket.connect(endpoint)

    window_base = args.window_prefix.strip() or "IsaacCam"
    concat_window = f"{window_base}-concat"
    cv2.namedWindow(concat_window, cv2.WINDOW_NORMAL)

    view_names = args.views
    split_windows = []
    if args.show_split:
        for name in view_names:
            win_name = f"{window_base}-{name}"
            cv2.namedWindow(win_name, cv2.WINDOW_NORMAL)
            split_windows.append(win_name)

    try:
        while True:
            try:
                msg = socket.recv(flags=zmq.NOBLOCK)
            except zmq.Again:
                cv2.waitKey(1)
                continue

            encoded = np.frombuffer(msg, dtype=np.uint8)
            frame = cv2.imdecode(encoded, cv2.IMREAD_COLOR)
            if frame is None:
                print("[viewer] Failed to decode frame; skipping.")
                continue

            cv2.imshow(concat_window, frame)

            if args.show_split and split_windows:
                views = split_views(frame, view_names)
                for win_name, view in zip(split_windows, views):
                    cv2.imshow(win_name, view)

            key = cv2.waitKey(1) & 0xFF
            if key in (ord("q"), 27):
                break
    except KeyboardInterrupt:
        pass
    finally:
        cv2.destroyAllWindows()
        socket.close(0)
        context.term()
        print("[viewer] Closed viewer.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
