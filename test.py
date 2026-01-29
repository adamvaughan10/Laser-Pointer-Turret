import logging
import time

import servo_controller as sc

logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")

STEP_DELAY = 1

# def test_navigate_to_target():
#     logger.info("test_navigate_to_target: setup GPIO")
#     pwm1, pwm2 = sc.init_gpio()
#     sc.pwm1 = pwm1
#     sc.pwm2 = pwm2

#     try:
#         logger.info("test_navigate_to_target: startup")
#         angles = sc.startup(pwm1, pwm2)

#         # Test moving from (0, 0) to (10, 10)
#         logger.info("test_navigate_to_target: move (0,0) -> (10,10)")
#         get_position = make_position_simulator((0, 0), (10, 10), step=5)
#         final_location = sc.navigate_to_target(get_position, (10, 10), angles, tolerance=1, step=5, max_steps=10)
#         logger.info("test_navigate_to_target: final location %s", final_location)
#         assert final_location is not None
#         assert abs(final_location[0] - 10) <= 1
#         assert abs(final_location[1] - 10) <= 1

#         # Test moving from (20, 20) to (5, 5)
#         logger.info("test_navigate_to_target: move (20,20) -> (5,5)")
#         get_position = make_position_simulator((20, 20), (5, 5), step=5)
#         final_location = sc.navigate_to_target(get_position, (5, 5), angles, tolerance=1, step=5, max_steps=20)
#         logger.info("test_navigate_to_target: final location %s", final_location)
#         assert final_location is not None
#         assert abs(final_location[0] - 5) <= 1
#         assert abs(final_location[1] - 5) <= 1

#     finally:
#         logger.info("test_navigate_to_target: cleanup GPIO")
#         sc.cleanup_gpio(pwm1, pwm2)

def test_move_both():
    logger.info("test_move_both: setup GPIO")
    pwm1, pwm2 = sc.init_gpio()
    sc.pwm1 = pwm1
    sc.pwm2 = pwm2

    try:
        logger.info("test_move_both: startup")

        # Move up (increase y)
        angle_x, angle_y = sc.center(pwm1, pwm2)
        logger.info("test_move_both: recentered x=%s y=%s", angle_x, angle_y)
        time.sleep(STEP_DELAY)
        logger.info("test_move_both: move up")
        up_x, up_y = sc.move_both(
            (angle_x, angle_y),
            (50, 50),
            (50, 70),
            step=5,
            steps=5,
            step_delay=0.05,
        )
        logger.info("test_move_both: after up x=%s y=%s", up_x, up_y)
        assert up_y >= angle_y
        time.sleep(STEP_DELAY)

        # Move down (decrease y)
        angle_x, angle_y = sc.center(pwm1, pwm2)
        logger.info("test_move_both: recentered x=%s y=%s", angle_x, angle_y)
        time.sleep(STEP_DELAY)
        logger.info("test_move_both: move down")
        down_x, down_y = sc.move_both(
            (angle_x, angle_y),
            (50, 70),
            (50, 50),
            step=5,
            steps=5,
            step_delay=0.05,
        )
        logger.info("test_move_both: after down x=%s y=%s", down_x, down_y)
        assert down_y <= angle_y
        time.sleep(STEP_DELAY)

        # Move right (increase x)
        angle_x, angle_y = sc.center(pwm1, pwm2)
        logger.info("test_move_both: recentered x=%s y=%s", angle_x, angle_y)
        time.sleep(STEP_DELAY)
        logger.info("test_move_both: move right")
        right_x, right_y = sc.move_both(
            (angle_x, angle_y),
            (50, 50),
            (70, 50),
            step=5,
            steps=5,
            step_delay=0.05,
        )
        logger.info("test_move_both: after right x=%s y=%s", right_x, right_y)
        assert right_x >= angle_x
        time.sleep(STEP_DELAY)

        # Move left (decrease x)
        angle_x, angle_y = sc.center(pwm1, pwm2)
        logger.info("test_move_both: recentered x=%s y=%s", angle_x, angle_y)
        time.sleep(STEP_DELAY)
        logger.info("test_move_both: move left")
        left_x, left_y = sc.move_both(
            (angle_x, angle_y),
            (70, 50),
            (50, 50),
            step=5,
            steps=5,
            step_delay=0.05,
        )
        logger.info("test_move_both: after left x=%s y=%s", left_x, left_y)
        assert left_x <= angle_x
        time.sleep(STEP_DELAY)

    finally:
        logger.info("test_move_both: cleanup GPIO")
        sc.cleanup_gpio(pwm1, pwm2)

def run_all_tests():
    # test_navigate_to_target()
    test_move_both()

if __name__ == "__main__":
    run_all_tests()
    logger.info("All tests completed successfully.")
