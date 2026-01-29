import time

from gpiozero import AngularServo, Device

try:
    from gpiozero.pins.lgpio import LGPIOFactory
except ImportError:
    LGPIOFactory = None

SERVO1_PIN = 18  #y-axis
SERVO2_PIN = 17  #x-axis
TOP_MIN = 75
TOP_MAX = 165
BOTTOM_MIN = 40
BOTTOM_MAX = 160
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
    current_x, current_y = get_position()

    for _ in range(max_steps):
        current = get_position()
        if current is None:
            return None
        current_x, current_y = current

        if abs(current_x - target_x) <= tolerance and abs(current_y - target_y) <= tolerance:
            return (angle_x, angle_y)

        # Move vertically if needed
        if abs(current_y - target_y) > tolerance:
            angle_y = move_vert(angle_y, current_y, target_y, step=step)
    
        # Move horizontally if needed
        if abs(current_x - target_x) > tolerance:
            angle_x = move_horiz(angle_x, current_x, target_x, step=step)

    return (angle_x, angle_y)

def move_vert(current_angle, current_y, target_y, step=2):
    direction = 1 if target_y > current_y else -1
    # next_y = current_y + direction * step
    # if direction > 0:
    #     next_y = min(next_y, target_y)
    # else:
    #     next_y = max(next_y, target_y)
    # next_y = max(BOTTOM_MIN, min(BOTTOM_MAX, next_y))
    next_angle = current_angle + direction * step
    duty = angle_to_duty(next_angle)
    pwm2.ChangeDutyCycle(duty)
    time.sleep(0.05)
    pwm2.ChangeDutyCycle(0)  # stop jitter
    return next_angle

def move_horiz(current_angle, current_x, target_x, step=2):
    direction = 1 if target_x > current_x else -1
    # next_x = current_x + direction * step
    # if direction > 0:
    #     next_x = min(next_x, target_x)
    # else:
    #     next_x = max(next_x, target_x)
    # next_x = max(TOP_MIN, min(TOP_MAX, next_x))
    next_angle = current_angle + direction * step
    duty = angle_to_duty(next_angle)
    pwm1.ChangeDutyCycle(duty)
    time.sleep(0.05)
    pwm1.ChangeDutyCycle(0)  # stop jitter
    return next_angle

def center(pwm1, pwm2):
    # Move to center position
    center1 = (TOP_MIN + TOP_MAX) // 2
    center2 = (BOTTOM_MIN + BOTTOM_MAX) // 2
    duty1 = angle_to_duty(center1)
    duty2 = angle_to_duty(center2)
    pwm1.ChangeDutyCycle(duty1)
    pwm2.ChangeDutyCycle(duty2)
    time.sleep(1)
    pwm1.ChangeDutyCycle(0)
    pwm2.ChangeDutyCycle(0)
    return center2, center1 # return current angles
