import argparse

import cv2


WINDOW_NAME = "Camera Feed"


def on_mouse(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        param["last_click"] = (x, y)
        print(f"Clicked at: x={x}, y={y}")


def main():
    parser = argparse.ArgumentParser(description="View camera feed and click to get coordinates.")
    parser.add_argument("--index", type=int, default=0, help="Camera index for cv2.VideoCapture.")
    parser.add_argument("--width", type=int, default=0, help="Optional capture width.")
    parser.add_argument("--height", type=int, default=0, help="Optional capture height.")
    args = parser.parse_args()

    cap = cv2.VideoCapture(args.index)
    if args.width > 0:
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, args.width)
    if args.height > 0:
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, args.height)

    if not cap.isOpened():
        raise RuntimeError(f"Could not open camera index {args.index}")

    state = {"last_click": None}
    cv2.namedWindow(WINDOW_NAME)
    cv2.setMouseCallback(WINDOW_NAME, on_mouse, state)

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to read frame from camera.")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        _, bw = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY)
        display = cv2.cvtColor(bw, cv2.COLOR_GRAY2BGR)

        moments = cv2.moments(bw, binaryImage=True)
        if moments["m00"] != 0:
            cx = int(moments["m10"] / moments["m00"])
            cy = int(moments["m01"] / moments["m00"])
            cv2.circle(display, (cx, cy), 6, (0, 0, 255), 2)
            cv2.putText(
                display,
                f"center=({cx}, {cy})",
                (cx + 10, cy - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 0, 255),
                1,
                cv2.LINE_AA,
            )

        if state["last_click"] is not None:
            x, y = state["last_click"]
            if 0 <= x < bw.shape[1] and 0 <= y < bw.shape[0]:
                brightness = int(bw[y, x])
                cv2.putText(
                    display,
                    f"bw={brightness}",
                    (x + 10, y + 15),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0, 255, 255),
                    1,
                    cv2.LINE_AA,
                )
            cv2.circle(display, (x, y), 5, (0, 255, 0), 2)
            cv2.putText(
                display,
                f"({x}, {y})",
                (x + 10, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 0),
                1,
                cv2.LINE_AA,
            )

        cv2.imshow(WINDOW_NAME, display)
        key = cv2.waitKey(1) & 0xFF
        if key in (ord("q"), 27):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
