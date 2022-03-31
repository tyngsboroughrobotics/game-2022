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
    libwallaby.camera_open()

    # wheels.drive(Direction.forward, cm(50))
    # return

    # dispense_poms([Color.red, Color.green, Color.green])
    # return

    # Collect the first three poms

    colors = []

    for angle in [0, 35, 55]:
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
    wheels.turn(TurnDirection.right, 70)

    # Drive to and line up with the sorter
    wheels.drive(Direction.forward, m(1.5))
    wheels.turn(TurnDirection.left, 90)
    wheels.drive(Direction.forward, cm(18))
    wheels.turn(TurnDirection.right, 95)  # not exactly 45 because of wheel offset

    raise_arm_halfway()
    wheels.drive(Direction.forward, cm(10))
    dispense_poms(colors)

    return

    # Collect the next three poms

    colors = []

    def collect_poms():
        lower_arm()

        for _ in range(3):
            color = collect_pom()

            if color:
                colors.append(color)

        raise_arm()

    _, distance_traveled_collecting_poms = get_wheel_distance_after(collect_poms)

    raise_arm()
    wheels.drive(Direction.forward, m(1.6) - distance_traveled_collecting_poms)

    print("COLORS:", colors)

    return

    dispense_poms(colors)


def raise_arm():
    arm_servo.set(420)


def raise_arm_halfway():
    arm_servo.set(540)


def lower_arm():
    arm_servo.set(660)


def collect_pom():
    for _ in range(10):
        libwallaby.camera_update()

    left_velocity = calculate_velocity(
        wheels.left_motor.speed, Direction.forward, wheels.left_offset
    )
    right_velocity = calculate_velocity(
        wheels.right_motor.speed, Direction.forward, wheels.right_offset
    )

    libwallaby.move_at_velocity(wheels.left_motor.port, left_velocity)
    libwallaby.move_at_velocity(wheels.right_motor.port, right_velocity)

    libwallaby.motor(spinner_motor.port, 100)

    timeout = 5
    run_until_poms(None, timeout=timeout)
    wheels.force_stop()

    wheels.drive(Direction.forward, cm(10))

    # Keep trying to pull in the pom pom until it's secured in the shaft
    color = None
    start = time.time()
    while time.time() - start <= timeout:
        libwallaby.camera_update()

        if libwallaby.get_object_count(red_channel) > 0:
            color = Color.red
        elif libwallaby.get_object_count(green_channel) > 0:
            color = Color.green
        elif color:
            break

    libwallaby.off(spinner_motor.port)

    return color


def dispense_poms(colors):
    raise_arm_halfway()

    for color in reversed(colors):
        if color == Color.red:
            direction = TurnDirection.left
        else:
            direction = TurnDirection.right

        angle = 30

        wheels.turn(direction, angle)

        # Give the poms a shake so the pom at the front rolls down into place

        shake_angle = 3.5

        for _ in range(5):
            wheels.turn(TurnDirection.left, shake_angle)
            wheels.turn(TurnDirection.right, shake_angle)

        wheels.turn(TurnDirection.left, shake_angle)
        libwallaby.msleep(500)

        # Dispense the pom

        libwallaby.motor(spinner_motor.port, -100)
        libwallaby.msleep(800)
        libwallaby.off(spinner_motor.port)
        libwallaby.msleep(100)

        # Reset position

        wheels.turn(direction.toggle(), angle)


def run_until_poms(f, timeout):
    start = time.time()
    while time.time() - start <= timeout:
        libwallaby.camera_update()

        if f:
            f()

        if (
            libwallaby.get_object_count(red_channel) > 0
            or libwallaby.get_object_count(green_channel) > 0
        ):
            break


def run_until_no_poms(f, timeout):
    start = time.time()
    while time.time() - start <= timeout:
        libwallaby.camera_update()

        if f:
            f()

        if (
            libwallaby.get_object_count(red_channel) == 0
            and libwallaby.get_object_count(green_channel) == 0
        ):
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
