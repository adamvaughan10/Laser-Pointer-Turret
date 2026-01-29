import RPi.GPIO as GPIO
import time

SERVO1_PIN = 18  # BCM numbering
SERVO2_PIN = 17
TOP_MIN = 75
TOP_MAX = 165
BOTTOM_MIN = 40
BOTTOM_MAX = 160

def angle_to_duty(angle):
    """
    Convert angle (0–180) to duty cycle.
    MG995 typically works well with ~2.5–12.5%.
    """
    return 2.5 + (angle / 180.0) * 10.0

def init_gpio():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(SERVO1_PIN, GPIO.OUT)
    GPIO.setup(SERVO2_PIN, GPIO.OUT)

    # 50 Hz PWM (20 ms period)
    pwm1 = GPIO.PWM(SERVO1_PIN, 50)
    pwm2 = GPIO.PWM(SERVO2_PIN, 50)
    pwm1.start(0)
    pwm2.start(0)
    return pwm1, pwm2

def cleanup_gpio(pwm1, pwm2):
    pwm1.stop()
    pwm2.stop()
    GPIO.cleanup()

def navigate_to_target(current_location, target_location, tolerance=2, step=2):
    """
    current_location: tuple (x, y)
    target_location: tuple (x, y)
    """

    current_x, current_y = current_location
    target_x, target_y = target_location

    while abs(current_x - target_x) > tolerance or abs(current_y - target_y) > tolerance:

        # Move vertically if needed
        if abs(current_y - target_y) > tolerance:
            current_y = move_vert(current_y, target_y, step=step, tolerance=tolerance)

        # Move horizontally if needed
        if abs(current_x - target_x) > tolerance:
            current_x = move_horiz(current_x, target_x, step=step, tolerance=tolerance)

    return (current_x, current_y)

def move_vert(current_y, target_y, step=2):
    direction = 1 if target_y > current_y else -1
    next_y = current_y + direction * step
    if direction > 0:
        next_y = min(next_y, target_y)
    else:
        next_y = max(next_y, target_y)
    next_y = max(BOTTOM_MIN, min(BOTTOM_MAX, next_y))
    duty = angle_to_duty(next_y)
    pwm2.ChangeDutyCycle(duty)
    time.sleep(0.05)
    pwm2.ChangeDutyCycle(0)  # stop jitter
    return next_y

def move_horiz(current_x, target_x, step=2):
    direction = 1 if target_x > current_x else -1
    next_x = current_x + direction * step
    if direction > 0:
        next_x = min(next_x, target_x)
    else:
        next_x = max(next_x, target_x)
    next_x = max(TOP_MIN, min(TOP_MAX, next_x))
    duty = angle_to_duty(next_x)
    pwm1.ChangeDutyCycle(duty)
    time.sleep(0.05)
    pwm1.ChangeDutyCycle(0)  # stop jitter
    return next_x
