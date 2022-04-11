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
    left_offset=0.97,  # if <1, veers to the right
    right_offset=1.0,  # if <1, veers to the left
)


class Color(Enum):
    red = 0
    green = 1


def main():
    libwallaby.camera_close()
    libwallaby.camera_open()

    raise_arm_halfway()

    # for _ in range(4):
    #     spin_once(Direction.forward)
    # libwallaby.msleep(1000)
    # for _ in range(4):
    #     spin_once(Direction.reverse)
    # return

    # wheels.drive(Direction.forward, cm(50))
    # return

    # dispense_poms([Color.red, Color.green, Color.green])
    # return

    # Collect the first group of poms

    # collect_group()
    # return

    # Collect the first two poms

    """
    colors = []

    for angle in [0, 35]:
        wheels.turn(TurnDirection.right, angle)

        lower_arm()

        color = with_reset_wheels(collect_pom)

        if color:
            colors.append(color)

        raise_arm()

        wheels.turn(TurnDirection.left, angle)

    # Turn in increments to avoid hitting the wall
    wheels.turn(TurnDirection.right, 35)
    wheels.drive(Direction.forward, cm(5))
    wheels.turn(TurnDirection.right, 55)

    # Drive to and line up with the sorter
    wheels.drive(Direction.forward, m(1.5))
    wheels.turn(TurnDirection.left, 90)
    wheels.drive(Direction.forward, cm(28))
    wheels.turn(TurnDirection.right, 95)  # not exactly 45 because of wheel offset

    raise_arm_halfway()
    wheels.drive(Direction.forward, cm(5))
    dispense_poms(colors)
    """

    dispense_poms([Color.red, Color.green, Color.red])

    return

    # Collect the next three poms

    colors = []

    def collect_poms():
        for _ in range(3):
            color = collect_pom()
            if color:
                colors.append(color)

    _, distance_traveled_collecting_poms = get_wheel_distance_after(collect_poms)

    print("COLORS:", colors)

    raise_arm()
    wheels.drive(Direction.forward, m(1.5) - distance_traveled_collecting_poms)
    dispense_poms(colors)


def raise_arm():
    arm_servo.set(420)


def raise_arm_halfway():
    arm_servo.set(580)


def lower_arm():
    arm_servo.set(700)


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


def collect_pom():
    raise_arm()

    wheels.start(Direction.forward)
    while not pom_detected():
        pass
    wheels.stop()

    color = detect_color()

    lower_arm()

    spinner_motor.start(Direction.forward)
    wheels.drive(Direction.forward, cm(10))
    libwallaby.msleep(1000)
    spinner_motor.stop()

    return color


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
        wheels.turn(TurnDirection.right, shake_angle)


def pom_detected():
    return libwallaby.analog(0) >= 1650


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
