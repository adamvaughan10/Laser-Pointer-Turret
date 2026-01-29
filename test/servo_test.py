import time

import servo_controller as sc

SERVO1_PIN = 18  # BCM numbering
SERVO2_PIN = 17
TOP_MIN = 75
TOP_MAX = 165
BOTTOM_MIN = 40
BOTTOM_MAX = 160
MOVE_STEPS = 10
MOVE_STEP_DELAY = 0.05

def angle_to_duty(angle):
    """
    Convert angle (0–180) to duty cycle.
    MG995 typically works well with ~2.5–12.5%.
    """
    return sc.angle_to_duty(angle)

def init_gpio():
    return sc.init_gpio()

def cleanup_gpio(pwm1, pwm2):
    sc.cleanup_gpio(pwm1, pwm2)

def move_both(pwm1, current1, target1, pwm2, current2, target2, steps, step_delay):
    for i in range(1, steps + 1):
        pos1 = current1 + (target1 - current1) * (i / steps)
        pos2 = current2 + (target2 - current2) * (i / steps)
        pwm1.ChangeDutyCycle(angle_to_duty(pos1))
        pwm2.ChangeDutyCycle(angle_to_duty(pos2))
        time.sleep(step_delay)

    pwm1.ChangeDutyCycle(0)  # stop jitter
    pwm2.ChangeDutyCycle(0)  # stop jitter
    return target1, target2

def prompt_angle(name, min_angle, max_angle):
    while True:
        raw = input(f"Enter {name} angle ({min_angle}-{max_angle}) or q to quit: ").strip().lower()
        if raw in ("q", "quit", "exit"):
            return None
        try:
            angle = int(raw)
        except ValueError:
            print(f"Please enter a whole number between {min_angle} and {max_angle}.")
            continue
        if min_angle <= angle <= max_angle:
            return angle
        print(f"Angle must be between {min_angle} and {max_angle}.")

def main(pwm1, pwm2):
    print("Servo coordinate entry. Press q to quit.")
    start1 = (TOP_MIN + TOP_MAX) // 2
    start2 = (BOTTOM_MIN + BOTTOM_MAX) // 2
    current1, current2 = move_both(
        pwm1, start1, start1, pwm2, start2, start2, MOVE_STEPS, MOVE_STEP_DELAY
    )
    print("Moved to start")
    try:
        while True:
            top_input = prompt_angle("Top", 0, 90)
            if top_input is None:
                break
            bottom_input = prompt_angle("Bottom", 0, 120)
            if bottom_input is None:
                break
            target1 = TOP_MAX - top_input
            target2 = BOTTOM_MIN + bottom_input
            current1, current2 = move_both(
                pwm1, current1, target1, pwm2, current2, target2, MOVE_STEPS, MOVE_STEP_DELAY
            )
            time.sleep(0.1)
            print("Move successful.")
    except KeyboardInterrupt:
        pass
    return current1, current2, start1, start2

if __name__ == "__main__":
    pwm1, pwm2 = init_gpio()
    start1 = (TOP_MIN + TOP_MAX) // 2
    start2 = (BOTTOM_MIN + BOTTOM_MAX) // 2
    current1 = start1
    current2 = start2
    try:
        current1, current2, start1, start2 = main(pwm1, pwm2)
    except KeyboardInterrupt:
        pass
    finally:
        move_both(pwm1, current1, start1, pwm2, current2, start2, MOVE_STEPS, MOVE_STEP_DELAY)
        cleanup_gpio(pwm1, pwm2)
