import argparse

import servo_controller as sc


def parse_args():
    parser = argparse.ArgumentParser(
        description="Interactive rig to test move_vert/move_horiz/navigate_to_target."
    )
    parser.add_argument("--start-x", type=int, default=None, help="Starting X position.")
    parser.add_argument("--start-y", type=int, default=None, help="Starting Y position.")
    parser.add_argument("--step", type=int, default=2, help="Step size per move.")
    parser.add_argument("--tolerance", type=int, default=2, help="Tolerance for navigate_to_target.")
    parser.add_argument(
        "--sequence",
        type=str,
        default="",
        help='Scripted sequence, e.g. "g 120 90; h 130; v 80"',
    )
    return parser.parse_args()


def main():
    args = parse_args()
    start_x = args.start_x
    start_y = args.start_y

    if start_x is None:
        start_x = (sc.TOP_MIN + sc.TOP_MAX) // 2
    if start_y is None:
        start_y = (sc.BOTTOM_MIN + sc.BOTTOM_MAX) // 2

    pwm1 = None
    pwm2 = None

    try:
        pwm1, pwm2 = sc.init_gpio()
        sc.pwm1 = pwm1
        sc.pwm2 = pwm2

        current_x = start_x
        current_y = start_y

        print("Servo move rig")
        print("Commands:")
        print("  g <x> <y>   move to target using navigate_to_target")
        print("  h <x>       move horizontal only (move_horiz)")
        print("  v <y>       move vertical only (move_vert)")
        print("  q           quit")
        print(f"Start: ({current_x}, {current_y}) step={args.step} tol={args.tolerance}")

        if args.sequence:
            commands = [cmd.strip() for cmd in args.sequence.split(";") if cmd.strip()]
        else:
            commands = None

        while True:
            if commands is not None:
                if not commands:
                    break
                line = commands.pop(0)
                print(f"cmd> {line}")
            else:
                line = input("cmd> ").strip()
            if not line:
                continue
            if line in ("q", "quit", "exit"):
                break

            parts = line.split()
            cmd = parts[0].lower()

            try:
                if cmd == "g" and len(parts) == 3:
                    target_x = int(parts[1])
                    target_y = int(parts[2])
                    current_x, current_y = sc.navigate_to_target(
                        (current_x, current_y),
                        (target_x, target_y),
                        tolerance=args.tolerance,
                        step=args.step,
                    )
                elif cmd == "h" and len(parts) == 2:
                    target_x = int(parts[1])
                    current_x = sc.move_horiz(current_x, target_x, step=args.step)
                elif cmd == "v" and len(parts) == 2:
                    target_y = int(parts[1])
                    current_y = sc.move_vert(current_y, target_y, step=args.step)
                else:
                    print("Invalid command. Use g x y | h x | v y | q")
                    continue
            except ValueError:
                print("Invalid number. Use integers for targets.")
                continue

            print(f"Current: ({current_x}, {current_y})")
    finally:
        if pwm1 is not None and pwm2 is not None:
            sc.cleanup_gpio(pwm1, pwm2)


if __name__ == "__main__":
    main()
