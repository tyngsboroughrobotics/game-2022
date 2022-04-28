import time

from lib.libwallaby import libwallaby
from lib.wheels import *

red_channel = 0
green_channel = 1

arm_servo = Servo(port=0, delay=20)

spinner_motor = Motor(port=2, speed=1)

wheels = Wheels(
    left_motor=Motor(port=0, speed=1),
    right_motor=Motor(port=1, speed=1),
    left_offset=0.91,  # if <1, veers to the right
    right_offset=1.0,  # if <1, veers to the left
)


half_turn = 150  # instead of 180 to counter offset


class Color(Enum):
    red = 0
    green = 1


def main():
    libwallaby.camera_close()
    libwallaby.camera_open()

    raise_arm()

    """
    # Collect only the red poms

    number_of_poms = 7
    distance_between_poms = inches(5.25)
    target_color = Color.red

    for _ in range(number_of_poms):
        wheels.turn(TurnDirection.left, 86)  # instead of 90 to counter offset

        def collect():
            wheels.start(Direction.forward)
            run_until_poms(None, timeout=3)
            wheels.stop()

            wheels.drive(Direction.forward, cm(1))

            color = detect_color()
            print("COLOR:", color, flush=True)

            if color == target_color:
                lower_arm()
                collect_pom()
                raise_arm()

        with_reset_wheels(collect)

        wheels.turn(TurnDirection.right, 80)  # instead of 90 to counter offset

        wheels.drive(Direction.forward, distance_between_poms)

    # Wait for Create

    # TODO

    # Drive to the material transport

    wheels.drive(Direction.forward, m(0.5))
    wheels.turn(TurnDirection.left, 90)
    wheels.drive(Direction.forward, cm(27))
    wheels.turn(TurnDirection.right, 90)

    # Dispense the red poms

    # TODO: TURN LEFT
    dispense_poms_v2()

    # Turn around

    wheels.turn(TurnDirection.right, half_turn)
    wheels.drive(Direction.forward, m(0.45))

    # Collect the remaining (green) poms

    lower_arm()

    spinner_motor.start(Direction.forward)
    wheels.drive(Direction.forward, m(0.85))
    libwallaby.msleep(500)
    spinner_motor.stop()

    raise_arm()

    # Turn around and drive to the material transport

    wheels.turn(TurnDirection.right, half_turn)
    wheels.drive(Direction.forward, m(1.3))
    """

    # Dispense the green poms

    # TODO: TURN RIGHT
    dispense_poms_v2()

    # TODO


def dispense_poms_v2():
    raise_arm_halfway()
    spinner_motor.start(Direction.reverse)

    for _ in range(5):
        shake()

    spinner_motor.stop()
    raise_arm()


def raise_arm():
    arm_servo.set(420)


def raise_arm_halfway():
    arm_servo.set(620)


def lower_arm():
    arm_servo.set(680)


def collect_group():
    colors = []

    lower_arm()

    color = with_reset_wheels(collect_pom)
    if color:
        colors.append(color)

    wheels.turn(TurnDirection.right, 90)
    wheels.drive(Direction.forward, cm(10))
    wheels.turn(TurnDirection.left, 90)

    def collect_2():
        for _ in range(2):
            color = collect_pom()
            if color:
                colors.append(color)

    with_reset_wheels(collect_2)


def detect_pom():
    wheels.start(Direction.forward)
    while not pom_detected():
        pass
    wheels.stop()

    return detect_color()


def collect_pom():
    spinner_motor.start(Direction.forward)
    wheels.drive(Direction.forward, cm(10))
    libwallaby.msleep(1000)
    spinner_motor.stop()


def detect_color():
    for _ in range(10):
        libwallaby.camera_update()

    red_area = total_area_of_color(red_channel)
    green_area = total_area_of_color(green_channel)

    if red_area > green_area:
        return Color.red
    elif green_area > red_area:
        return Color.green
    else:
        return None


def total_area_of_color(channel):
    object_count = libwallaby.get_object_count(channel)
    area = 0

    for object in range(object_count):
        area += libwallaby.get_object_area(channel, object)

    return area


def wait_until_new_pom(channel):
    prev_total_area = total_area_of_color(channel)

    while True:
        total_area = total_area_of_color(channel)

        if total_area > prev_total_area + 500:
            break


def dispense_poms(colors):
    raise_arm_halfway()

    for color in reversed(colors):
        if color == Color.red:
            direction = TurnDirection.left
            channel = red_channel
        else:
            direction = TurnDirection.right
            channel = green_channel

        angle = 30

        wheels.turn(direction, angle)

        shake()
        libwallaby.msleep(500)

        # Dispense the pom

        spinner_motor.start(Direction.reverse)
        wait_until_new_pom(channel)
        spinner_motor.stop()
        libwallaby.msleep(100)

        # Reset position

        wheels.turn(direction.toggle(), angle)


def shake():
    shake_angle = 5

    for _ in range(5):
        wheels.turn(TurnDirection.left, shake_angle)
        raise_arm()
        wheels.turn(TurnDirection.right, shake_angle)
        raise_arm_halfway()


def pom_detected():
    libwallaby.camera_update()

    return (
        libwallaby.get_object_count(red_channel) > 0
        or libwallaby.get_object_count(green_channel) > 0
    )


def run_until_poms(f, timeout):
    start = time.time()
    while time.time() - start <= timeout:
        if f:
            f()

        if pom_detected():
            break


def run_until_no_poms(f, timeout):
    start = time.time()
    while time.time() - start <= timeout:
        if f:
            f()

        if not pom_detected():
            break


def with_reset_wheels(f, direction=Direction.reverse, padding=0):
    value, distance = get_wheel_distance_after(f)
    wheels.drive(direction, distance - padding)
    return value


def get_wheel_distance_after(f):
    initial_position_left = libwallaby.get_motor_position_counter(
        wheels.left_motor.port
    )
    initial_position_right = libwallaby.get_motor_position_counter(
        wheels.right_motor.port
    )

    value = f()

    final_position_left = libwallaby.get_motor_position_counter(wheels.left_motor.port)
    final_position_right = libwallaby.get_motor_position_counter(
        wheels.right_motor.port
    )

    left_distance = final_position_left - initial_position_left
    right_distance = final_position_right - initial_position_right

    return value, (
        (left_distance if left_distance < right_distance else right_distance)
        / motor_pwm_ticks
        / motor_travel_time_1_cm
    )
