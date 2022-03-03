#if __has_include(<kipr/wombat.h>)
#include <kipr/wombat.h>
#else
#error "Please compile on the Wombat"
#endif

#include <stdio.h>
#include <stdlib.h>
#include "wheels.h"

void raise_arm();
void lower_arm();
void reset_splitter();
void split_pom_left();
void split_pom_right();
void drive_until_centered(int channel);

const int red_channel = 0;
const int green_channel = 1;

const Servo arm_servo = {
    .port = 0,
};

const Servo splitter_servo = {
    .port = 1,
};

const Motor spinner_motor = {
    .port = 2,
    .speed = 1.0,
};

const Wheels wheels = {
    .left_motor = {
        .port = 0,
        .speed = 1.0,
    },
    .right_motor = {
        .port = 1,
        .speed = 1.0,
    },
    .left_offset = 0.9975, // if <1, veers to the right
    .right_offset = 1.0, // if <1, veers to the left
};

/*

lift arm

repeat 8 times:
    if green:
        move servo left
    else:
        move servo right
    move forward

lower arm

THEN: go back around to collect poms

*/

int main() {
    camera_open();
    raise_arm();
    reset_splitter();

    int pom_width = CM(2);
    int space_between_poms = IN(6) - pom_width;

    int initial_position_left = get_motor_position_counter(wheels.left_motor.port);
    int initial_position_right = get_motor_position_counter(wheels.right_motor.port);

    for (int i = 0; i < 5; i++) {
        // Update multiple times to get better accuracy
        for (int i = 0; i < 10; i++) {
            camera_update();
        }

        int pom_is_red = get_object_count(red_channel) > 0;

        if (pom_is_red) {
            // Red pom
            printf("Red!\n"); fflush(stdout);
            split_pom_right();
            drive_until_centered(red_channel);
            split_pom_left();
        } else {
            // Green pom
            printf("Green!\n"); fflush(stdout);
            split_pom_left();
            drive_until_centered(green_channel);
            split_pom_right();
        }

        reset_splitter();

        drive_wheels(wheels, FORWARD, space_between_poms);

        // msleep(5000); // FIXME: TEMPORARY
    }

    msleep(2000); // FIXME: TEMPORARY

    // Go back and collect the poms
    // TODO: Put into function

    int final_position_left = get_motor_position_counter(wheels.left_motor.port);
    int final_position_right = get_motor_position_counter(wheels.right_motor.port);

    int left_distance = final_position_left - initial_position_left;
    int right_distance = final_position_right - initial_position_right;

    int distance = (left_distance < right_distance ? left_distance : right_distance) / MOTOR_PWM_TICKS / MOTOR_TRAVEL_TIME_1_CM;

    drive_wheels(wheels, REVERSE, distance - CM(15));

    turn_wheels(wheels, LEFT, 120);
    drive_wheels(wheels, FORWARD, CM(22));
    turn_wheels(wheels, RIGHT, 120);

    lower_arm();

    motor(spinner_motor.port, 100);
    drive_wheels(wheels, FORWARD, space_between_poms * 3);
    off(spinner_motor.port);

    camera_close();

    return 0;
}

void raise_arm() {
    set_servo(arm_servo, 1040);
}

void lower_arm() {
    set_servo(arm_servo, 1250);
}

void reset_splitter() {
    set_servo(splitter_servo, 1280);
}

void split_pom_left() {
    set_servo(splitter_servo, 0);
}

void split_pom_right() {
    set_servo(splitter_servo, 2047);
}

void drive_until_centered(int channel) {
    int threshold = 10;
    int center_y = get_camera_height() / 2;

    int left_velocity = calculate_velocity(wheels.left_motor.speed, FORWARD, wheels.left_offset);
    int right_velocity = calculate_velocity(wheels.right_motor.speed, FORWARD, wheels.right_offset);

    move_at_velocity(wheels.left_motor.port, left_velocity);
    move_at_velocity(wheels.right_motor.port, right_velocity);

    int y = 0;
    do {
        camera_update();

        if (get_object_count(channel) > 0) {
            y = get_object_center_y(channel, 0);
        } else {
            break;
        }
    } while (abs(y - center_y) > threshold);

    force_stop_wheels(wheels);
}
