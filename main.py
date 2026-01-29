import argparse

import cv2

import camera_feed as cf
import servo_controller as sc


def main():
    parser = argparse.ArgumentParser(
        description="Run camera feed and move servos to new click locations."
    )
    parser.add_argument("--index", type=int, default=0, help="Camera index for cv2.VideoCapture.")
    parser.add_argument("--width", type=int, default=0, help="Optional capture width.")
    parser.add_argument("--height", type=int, default=0, help="Optional capture height.")
    args = parser.parse_args()

    state = {"last_click": None, "dot_center": None}
    cap = cf.init_camera(args.index, args.width, args.height)
    cf.setup_window(state)

    pwm1 = None
    pwm2 = None
    last_click_seen = None

    def get_position():
        ret, frame = cap.read()
        if not ret:
            return None
        display, _ = cf.process_frame(frame, state)
        cv2.imshow(cf.WINDOW_NAME, display)
        cv2.waitKey(1)
        return cf.get_current_dot_location(state)

    try:
        pwm1, pwm2 = sc.init_gpio()
        sc.pwm1 = pwm1
        sc.pwm2 = pwm2

        angles = sc.center(pwm1, pwm2)

        while True:
            ret, frame = cap.read()
            if not ret:
                print("Failed to read frame from camera.")
                break

            display, _ = cf.process_frame(frame, state)

            click = cf.get_last_click_location(state)
            if click is not None and click != last_click_seen:
                current = cf.get_current_dot_location(state)
                if current is None:
                    print("No dot detected; skipping navigate_to_target.")
                else:
                    sc.navigate_to_target(get_position, click, angles)
                last_click_seen = click

            cv2.imshow(cf.WINDOW_NAME, display)
            key = cv2.waitKey(1) & 0xFF
            if key in (ord("q"), 27):
                break
    finally:
        sc.center(pwm1, pwm2)
        cap.release()
        cv2.destroyAllWindows()
        if pwm1 is not None and pwm2 is not None:
            sc.cleanup_gpio(pwm1, pwm2)


if __name__ == "__main__":
    main()
