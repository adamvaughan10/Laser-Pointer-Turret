import servo_test as st
import time

TOP_MIN = st.TOP_MIN
TOP_MAX = st.TOP_MAX
BOTTOM_MIN = st.BOTTOM_MIN
BOTTOM_MAX = st.BOTTOM_MAX
DEMO_STEPS = 20
DEMO_STEP_DELAY = 0.05

pwm1 = None
pwm2 = None

def move_both_smooth(pwm1, current1, target1, pwm2, current2, target2, steps, step_delay):
    for i in range(1, steps + 1):
        pos1 = current1 + (target1 - current1) * (i / steps)
        pos2 = current2 + (target2 - current2) * (i / steps)
        pwm1.ChangeDutyCycle(st.angle_to_duty(pos1))
        pwm2.ChangeDutyCycle(st.angle_to_duty(pos2))
        time.sleep(step_delay)

    pwm1.ChangeDutyCycle(0)  # stop jitter
    pwm2.ChangeDutyCycle(0)  # stop jitter
    return target1, target2

def move_both_bottom_half_speed(pwm1, current1, target1, pwm2, current2, target2, steps, step_delay):
    bottom_steps = steps * 2
    for i in range(1, bottom_steps + 1):
        if i <= steps:
            pos1 = current1 + (target1 - current1) * (i / steps)
        else:
            pos1 = target1
        pos2 = current2 + (target2 - current2) * (i / bottom_steps)
        pwm1.ChangeDutyCycle(st.angle_to_duty(pos1))
        pwm2.ChangeDutyCycle(st.angle_to_duty(pos2))
        time.sleep(step_delay)

    pwm1.ChangeDutyCycle(0)  # stop jitter
    pwm2.ChangeDutyCycle(0)  # stop jitter
    return target1, target2

def demo_low_mid_high(current1, current2):
    low1 = TOP_MIN
    low2 = BOTTOM_MIN
    mid1 = (TOP_MIN + TOP_MAX) // 2
    mid2 = (BOTTOM_MIN + BOTTOM_MAX) // 2
    high1 = TOP_MAX
    high2 = BOTTOM_MAX

    current1, current2 = move_both_smooth(
        pwm1, current1, low1, pwm2, current2, low2, DEMO_STEPS, DEMO_STEP_DELAY
    )
    time.sleep(0.3)
    current1, current2 = move_both_smooth(
        pwm1, current1, mid1, pwm2, current2, mid2, DEMO_STEPS, DEMO_STEP_DELAY
    )
    time.sleep(0.3)
    current1, current2 = move_both_smooth(
        pwm1, current1, high1, pwm2, current2, high2, DEMO_STEPS, DEMO_STEP_DELAY
    )
    return current1, current2

def demo_full_range_loops(current1, current2):
    for _ in range(3):
        current1, current2 = move_both_smooth(
            pwm1, current1, TOP_MAX, pwm2, current2, BOTTOM_MAX, DEMO_STEPS, DEMO_STEP_DELAY
        )
        current1, current2 = move_both_smooth(
            pwm1, current1, TOP_MIN, pwm2, current2, BOTTOM_MIN, DEMO_STEPS, DEMO_STEP_DELAY
        )
    return current1, current2

def demo_bottom_half_speed(current1, current2):
    for _ in range(3):
        current1, current2 = move_both_bottom_half_speed(
            pwm1, current1, TOP_MAX, pwm2, current2, BOTTOM_MAX, DEMO_STEPS, DEMO_STEP_DELAY
        )
        current1, current2 = move_both_bottom_half_speed(
            pwm1, current1, TOP_MIN, pwm2, current2, BOTTOM_MIN, DEMO_STEPS, DEMO_STEP_DELAY
        )
    return current1, current2

def main():
    global pwm1, pwm2
    pwm1, pwm2 = st.init_gpio()
    print("Movement demo starting.")
    current1 = (TOP_MIN + TOP_MAX) // 2
    current2 = (BOTTOM_MIN + BOTTOM_MAX) // 2

    print("Demo 1: low -> mid -> high")
    current1, current2 = demo_low_mid_high(current1, current2)
    time.sleep(0.5)

    print("Demo 2: smooth full-range loops (3x)")
    current1, current2 = demo_full_range_loops(current1, current2)
    time.sleep(0.5)

    print("Demo 3: full-range loops with bottom at half speed (3x)")
    current1, current2 = demo_bottom_half_speed(current1, current2)

    return current1, current2

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
    finally:
        if pwm1 is not None and pwm2 is not None:
            st.cleanup_gpio(pwm1, pwm2)
