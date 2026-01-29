import logging

import servo_controller as sc

logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")

def test_navigate_to_target():
    logger.info("test_navigate_to_target: setup GPIO")
    pwm1, pwm2 = sc.init_gpio()
    sc.pwm1 = pwm1
    sc.pwm2 = pwm2

    try:
        logger.info("test_navigate_to_target: startup")
        angles = sc.startup(pwm1, pwm2)

        # Test moving from (0, 0) to (10, 10)
        logger.info("test_navigate_to_target: move (0,0) -> (10,10)")
        final_location = sc.navigate_to_target((0, 0), (10, 10), angles, tolerance=1, step=5)
        logger.info("test_navigate_to_target: final location %s", final_location)
        assert abs(final_location[0] - 10) <= 1
        assert abs(final_location[1] - 10) <= 1

        # Test moving from (20, 20) to (5, 5)
        logger.info("test_navigate_to_target: move (20,20) -> (5,5)")
        final_location = sc.navigate_to_target((20, 20), (5, 5), angles, tolerance=1, step=5)
        logger.info("test_navigate_to_target: final location %s", final_location)
        assert abs(final_location[0] - 5) <= 1
        assert abs(final_location[1] - 5) <= 1

    finally:
        logger.info("test_navigate_to_target: cleanup GPIO")
        sc.cleanup_gpio(pwm1, pwm2)

def test_move_vert():
    logger.info("test_move_vert: setup GPIO")
    pwm1, pwm2 = sc.init_gpio()
    sc.pwm1 = pwm1
    sc.pwm2 = pwm2

    try:
        logger.info("test_move_vert: startup")
        angles = sc.startup(pwm1, pwm2)

        # Test moving up
        logger.info("test_move_vert: move up")
        new_angle = sc.move_vert(90, 50, 70, step=5)
        logger.info("test_move_vert: new angle %s", new_angle)
        assert new_angle > 90

        # Test moving down
        logger.info("test_move_vert: move down")
        new_angle = sc.move_vert(90, 70, 50, step=5)
        logger.info("test_move_vert: new angle %s", new_angle)
        assert new_angle < 90

    finally:
        logger.info("test_move_vert: cleanup GPIO")
        sc.cleanup_gpio(pwm1, pwm2)

def test_move_horiz():
    logger.info("test_move_horiz: setup GPIO")
    pwm1, pwm2 = sc.init_gpio()
    sc.pwm1 = pwm1
    sc.pwm2 = pwm2

    try:
        logger.info("test_move_horiz: startup")
        angles = sc.startup(pwm1, pwm2)

        # Test moving right
        logger.info("test_move_horiz: move right")
        new_angle = sc.move_horiz(90, 50, 70, step=5)
        logger.info("test_move_horiz: new angle %s", new_angle)
        assert new_angle > 90

        # Test moving left
        logger.info("test_move_horiz: move left")
        new_angle = sc.move_horiz(90, 70, 50, step=5)
        logger.info("test_move_horiz: new angle %s", new_angle)
        assert new_angle < 90

    finally:
        logger.info("test_move_horiz: cleanup GPIO")
        sc.cleanup_gpio(pwm1, pwm2)
