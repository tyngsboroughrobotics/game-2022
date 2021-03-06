import time
from threading import Timer

from lib.libwallaby import libwallaby
from lib.wheels import *

red_channel = 0
green_channel = 1

arm_servo = Servo(port=0, delay=20)

spinner_motor = Motor(port=2, speed=1)

wheels = Wheels(
    left_motor=Motor(port=0, speed=1),
    right_motor=Motor(port=1, speed=1),
    left_offset=0.92,  # if <1, veers to the right
    right_offset=1.0,  # if <1, veers to the left
)


class Color(Enum):
    red = 0
    green = 1


half_rotation = 155  # instead of 180 to counter offset


def main():
    libwallaby.camera_close()  # to prevent segfaults when the camera is opened twice

    # Reset to initial positions -- the rings should be placed so the
    # Fisher-Price logo faces the robot
    libwallaby.camera_open()
    raise_arm()

    # Wait for the Create

    libwallaby.msleep(4000)

    # Knock the rings out of the way

    distance = m(0.6)
    wheels.drive(Direction.forward, distance)
    wheels.turn(TurnDirection.left, 15)  # to counter offset
    wheels.drive(Direction.reverse, distance / 2)
    wheels.turn(TurnDirection.left, 10)  # to counter offset
    wheels.drive(Direction.reverse, distance / 2 + cm(5))

    # Reposition inside the starting box

    wheels.drive(Direction.forward, cm(4))
    wheels.turn(TurnDirection.left, 90)
    wheels.drive(Direction.reverse, cm(21))
    wheels.turn(TurnDirection.right, 75)

    # Collect only the red poms

    number_of_poms = 8 - 1  # the first pom is skipped
    number_of_red_poms = 0
    distance_between_poms = inches(5.1)

    target_color = Color.red

    for _ in range(number_of_poms):
        wheels.turn(TurnDirection.left, 86)

        def collect():
            nonlocal number_of_red_poms

            drive_toward_pom()
            align_wheels_to_pom()

            wheels.drive(Direction.forward, cm(1))

            color = detect_color()
            print("COLOR:", color)

            if color == target_color:
                lower_arm()
                collect_pom()
                raise_arm()
                number_of_red_poms += 1

        with_reset_wheels(collect)

        wheels.turn(TurnDirection.right, 82)

        wheels.drive(Direction.forward, distance_between_poms)

    # Drive to the material transport

    wheels.drive(Direction.forward, m(0.5))
    wheels.turn(TurnDirection.left, 90)
    wheels.drive(Direction.forward, cm(25))
    wheels.turn(TurnDirection.right, 90)

    # Dispense the red poms

    dispense_poms()

    # Turn around

    wheels.turn(TurnDirection.right, half_rotation)
    wheels.drive(Direction.forward, m(0.4))

    # Collect the remaining (green) poms

    number_of_green_poms = number_of_poms - number_of_red_poms

    for _ in range(number_of_green_poms):
        drive_toward_pom()
        align_wheels_to_pom()

        wheels.drive(Direction.forward, cm(2))

        lower_arm()
        collect_pom()
        raise_arm()

    # Turn around and drive to the material transport

    wheels.turn(TurnDirection.right, half_rotation)
    wheels.drive(Direction.forward, m(1.3))

    # Dispense the green poms

    wheels.turn(TurnDirection.left, 30)
    dispense_poms()


def drive_toward_pom():
    wheels.left_motor.speed = 0.5
    wheels.right_motor.speed = 0.5

    wheels.start(Direction.forward)
    run_until_poms(None, timeout=5)
    wheels.stop()

    wheels.left_motor.speed = 1
    wheels.right_motor.speed = 1


def raise_arm():
    arm_servo.set(420)


def raise_arm_halfway():
    arm_servo.set(620)


def lower_arm():
    arm_servo.set(680)


def align_wheels_to_pom():
    color = detect_color()
    if color is None:
        return
    channel = channel_of(color)

    if libwallaby.get_object_count(channel) == 0:
        return

    center_x = libwallaby.get_camera_width() / 2
    threshold = 3

    prev_left_offset = wheels.left_offset
    prev_right_offset = wheels.right_offset

    wheels.left_motor.speed = 0.1
    wheels.right_motor.speed = 0.1
    wheels.left_offset = 1
    wheels.right_offset = 1

    while True:
        libwallaby.camera_update()

        diff = libwallaby.get_object_center_x(channel, 0) - center_x

        if diff < -threshold:
            wheels.start_turn(TurnDirection.left)
        elif diff > threshold:
            wheels.start_turn(TurnDirection.right)
        else:
            wheels.stop()
            break

    wheels.left_motor.speed = 1
    wheels.right_motor.speed = 1
    wheels.left_offset = prev_left_offset
    wheels.right_offset = prev_right_offset


def dispense_poms():
    raise_arm_halfway()
    spinner_motor.start(Direction.reverse)

    for _ in range(10):
        shake()

    spinner_motor.stop()
    raise_arm()


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
    wheels.start(Direction.forward)
    libwallaby.msleep(950)
    wheels.stop()
    libwallaby.msleep(600)
    spinner_motor.stop()


def detect_color():
    for _ in range(10):
        libwallaby.camera_update()

    if libwallaby.get_object_count(red_channel) > 0:
        return Color.red
    elif libwallaby.get_object_count(green_channel) > 0:
        return Color.green
    else:
        return None


def shake():
    shake_angle = 5

    for _ in range(5):
        wheels.turn(TurnDirection.left, shake_angle)
        wheels.turn(TurnDirection.right, shake_angle)

    # fix the offset
    wheels.turn(TurnDirection.right, shake_angle / 6)


def channel_of(color):
    if color == Color.red:
        return red_channel
    elif color == Color.green:
        return green_channel
    else:
        raise ValueError("expected color")


def pom_detected():
    for _ in range(10):
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
