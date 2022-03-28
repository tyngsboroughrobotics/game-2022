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
    left_offset=0.975,  # if <1, veers to the right
    right_offset=1.0,  # if <1, veers to the left
)


class Color(Enum):
    red = 0
    green = 1


def main():
    libwallaby.camera_open()

    # dispense_poms([Color.green, Color.red, Color.green])
    # return

    # TODO: Get in position

    colors = []

    def collect_poms():
        # The offset is more noticeable because the wheels stop and start
        # frequently
        prev_offset = wheels.left_offset
        wheels.left_offset -= 0.04
        lower_arm()

        for _ in range(3):
            color = collect_pom()

            if color:
                colors.append(color)

        raise_arm()
        wheels.left_offset = prev_offset

    distance_traveled_collecting_poms = get_wheel_distance_after(collect_poms)

    raise_arm()
    wheels.drive(Direction.forward, m(1.6) - distance_traveled_collecting_poms)

    print("COLORS:", colors)

    dispense_poms(colors)


def raise_arm():
    arm_servo.set(465)


def lower_arm():
    arm_servo.set(665)


def raise_arm_halfway():
    arm_servo.set(565)


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

        def shake():
            wheels.turn(TurnDirection.left, shake_angle)
            wheels.turn(TurnDirection.right, shake_angle)

        run_until_poms(shake, timeout=3)
        wheels.turn(TurnDirection.left, shake_angle)
        libwallaby.msleep(500)

        # Dispense the pom

        libwallaby.motor(spinner_motor.port, -100)
        libwallaby.msleep(500)
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
    wheels.drive(direction, get_wheel_distance_after(f) - padding)


def get_wheel_distance_after(f):
    initial_position_left = libwallaby.get_motor_position_counter(
        wheels.left_motor.port
    )
    initial_position_right = libwallaby.get_motor_position_counter(
        wheels.right_motor.port
    )

    f()

    final_position_left = libwallaby.get_motor_position_counter(wheels.left_motor.port)
    final_position_right = libwallaby.get_motor_position_counter(
        wheels.right_motor.port
    )

    left_distance = final_position_left - initial_position_left
    right_distance = final_position_right - initial_position_right

    return (
        (left_distance if left_distance < right_distance else right_distance)
        / motor_pwm_ticks
        / motor_travel_time_1_cm
    )
