import time

from gpiozero import AngularServo, Device

try:
    from gpiozero.pins.lgpio import LGPIOFactory
except ImportError:
    LGPIOFactory = None

SERVO1_PIN = 18  # top (y-axis)
SERVO2_PIN = 17  # bottom (x-axis)
TOP_CENTER = 120
BOTTOM_CENTER = 100
TOP_BOUND = 10
BOTTOM_BOUND = 10
SERVO_MIN_PULSE = 0.0005
SERVO_MAX_PULSE = 0.0025

pwm1 = None
pwm2 = None

def angle_to_duty(angle):
    """
    Convert angle (0–180) to duty cycle.
    MG995 typically works well with ~2.5–12.5%.
    """
    return 2.5 + (angle / 180.0) * 10.0

def duty_to_angle(duty):
    angle = (duty - 2.5) / 10.0 * 180.0
    return max(0.0, min(180.0, angle))

def clamp(value, top_or_bottom):
    if (top_or_bottom == "top"):
        min_value = TOP_CENTER - TOP_BOUND
        max_value = TOP_CENTER + TOP_BOUND
    else:
        min_value = BOTTOM_CENTER - BOTTOM_BOUND
        max_value = BOTTOM_CENTER + BOTTOM_BOUND
    return max(min_value, min(max_value, value))

class ServoAdapter:
    def __init__(self, servo):
        self._servo = servo

    def ChangeDutyCycle(self, duty):
        if duty <= 0:
            self._stop()
            return
        self._servo.angle = duty_to_angle(duty)

    def stop(self):
        self._stop()

    def close(self):
        self._servo.close()

    def _stop(self):
        if hasattr(self._servo, "detach"):
            self._servo.detach()
        else:
            try:
                self._servo.value = None
            except Exception:
                pass

def init_gpio():
    if LGPIOFactory is not None and not isinstance(Device.pin_factory, LGPIOFactory):
        Device.pin_factory = LGPIOFactory()

    servo1 = AngularServo(
        SERVO1_PIN,
        min_angle=0,
        max_angle=180,
        min_pulse_width=SERVO_MIN_PULSE,
        max_pulse_width=SERVO_MAX_PULSE,
    )
    servo2 = AngularServo(
        SERVO2_PIN,
        min_angle=0,
        max_angle=180,
        min_pulse_width=SERVO_MIN_PULSE,
        max_pulse_width=SERVO_MAX_PULSE,
    )
    return ServoAdapter(servo1), ServoAdapter(servo2)

def cleanup_gpio(pwm1, pwm2):
    if pwm1 is not None:
        pwm1.stop()
        if hasattr(pwm1, "close"):
            pwm1.close()
    if pwm2 is not None:
        pwm2.stop()
        if hasattr(pwm2, "close"):
            pwm2.close()

def navigate_to_target(get_position, target_location, current_angles, tolerance=3, step=2, max_steps=200):
    """
    get_position: callable returning current (x, y) or None
    target_location: tuple (x, y)
    """
    angle_x, angle_y = current_angles
    target_x, target_y = target_location

    for _ in range(max_steps):
        current = get_position()
        if current is None:
            return None
        current_x, current_y = current

        if abs(current_x - target_x) <= tolerance and abs(current_y - target_y) <= tolerance:
            return (angle_x, angle_y)

        angle_x, angle_y = move_both(
            (angle_x, angle_y),
            (current_x, current_y),
            (target_x, target_y),
            step=step,
            steps=1,
            step_delay=0.05,
        )

    return (angle_x, angle_y)

def move_both(current_angles, current_location, target_location, step=2, steps=10, step_delay=0.05):
    angle_x, angle_y = current_angles
    current_x, current_y = current_location
    target_x, target_y = target_location

    direction_x = 1 if target_x < current_x else -1 if target_x > current_x else 0
    direction_y = 1 if target_y > current_y else -1 if target_y < current_y else 0

    target_angle_x = clamp(
        angle_x + direction_x * step,
        top_or_bottom="bottom"
    )
    target_angle_y = clamp(
        angle_y + direction_y * step,
        top_or_bottom="top"
    )

    return move_both_angles(
        pwm1,
        angle_y,
        target_angle_y,
        pwm2,
        angle_x,
        target_angle_x,
        steps,
        step_delay,
    )
    

def move_both_angles(pwm1, current1, target1, pwm2, current2, target2, steps, step_delay):
    for i in range(1, steps + 1):
        pos1 = current1 + (target1 - current1) * (i / steps)
        pos2 = current2 + (target2 - current2) * (i / steps)
        pwm1.ChangeDutyCycle(angle_to_duty(pos1))
        pwm2.ChangeDutyCycle(angle_to_duty(pos2))
        time.sleep(step_delay)
        print(f"Moved to: top={pos1:.1f}, bottom={pos2:.1f}")

    pwm1.ChangeDutyCycle(0)  # stop jitter
    pwm2.ChangeDutyCycle(0)  # stop jitter
    return pos2, pos1  # return (angle_x, angle_y)

# def move_vert(current_angle, current_y, target_y, step=2):
#     direction = 1 if target_y > current_y else -1
#     # next_y = current_y + direction * step
#     # if direction > 0:
#     #     next_y = min(next_y, target_y)
#     # else:
#     #     next_y = max(next_y, target_y)
#     # next_y = max(BOTTOM_MIN, min(BOTTOM_MAX, next_y))
#     next_angle = clamp(
#         current_angle + direction * step,
#         BOTTOM_CENTER - BOTTOM_BOUND,
#         BOTTOM_CENTER + BOTTOM_BOUND,
#     )
#     duty = angle_to_duty(next_angle)
#     pwm2.ChangeDutyCycle(duty)
#     time.sleep(0.05)
#     pwm2.ChangeDutyCycle(0)  # stop jitter
#     return next_angle

# def move_horiz(current_angle, current_x, target_x, step=2):
    direction = 1 if target_x > current_x else -1
    # next_x = current_x + direction * step
    # if direction > 0:
    #     next_x = min(next_x, target_x)
    # else:
    #     next_x = max(next_x, target_x)
    # next_x = max(TOP_MIN, min(TOP_MAX, next_x))
    next_angle = clamp(
        current_angle + direction * step,
        TOP_CENTER - TOP_BOUND,
        TOP_CENTER + TOP_BOUND,
    )
    duty = angle_to_duty(next_angle)
    pwm1.ChangeDutyCycle(duty)
    time.sleep(0.05)
    pwm1.ChangeDutyCycle(0)  # stop jitter
    return next_angle

def center(pwm1, pwm2):
    # Move to center position
    duty1 = angle_to_duty(TOP_CENTER)
    duty2 = angle_to_duty(BOTTOM_CENTER)
    pwm1.ChangeDutyCycle(duty1)
    pwm2.ChangeDutyCycle(duty2)
    time.sleep(1)
    pwm1.ChangeDutyCycle(0)
    pwm2.ChangeDutyCycle(0)
    return BOTTOM_CENTER, TOP_CENTER  # return current angles (x,y)
