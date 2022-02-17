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
    .left_offset = 0.9,
    .right_offset = 1.0,
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

    int space_between_poms = IN(6);

    for (int i = 0; i < 5; i++) {
        // Update multiple times to get better accuracy
        for (int i = 0; i < 10; i++) {
            camera_update();
        }

        int pom_is_red = get_object_count(red_channel) > 0;
        int forward_distance = CM(8);

        if (pom_is_red) {
            // Red pom
            printf("Red!\n"); fflush(stdout);
            split_pom_right();
            drive_wheels(wheels, FORWARD, forward_distance);
            split_pom_left();
        } else {
            // Green pom
            printf("Green!\n"); fflush(stdout);
            split_pom_left();
            drive_wheels(wheels, FORWARD, forward_distance);
            split_pom_right();
        }

        reset_splitter();

        drive_wheels(wheels, FORWARD, space_between_poms - forward_distance - CM(1));

        // msleep(5000); // FIXME: TEMPORARY
    }

    msleep(2000); // FIXME: TEMPORARY

    // Go back and collect the poms
    // TODO: Put into function

    drive_wheels(wheels, REVERSE, space_between_poms * 4);

    turn_wheels(wheels, LEFT, 120);
    drive_wheels(wheels, FORWARD, CM(22));
    turn_wheels(wheels, RIGHT, 120);

    lower_arm();

    motor(spinner_motor.port, 100);
    drive_wheels(wheels, FORWARD, space_between_poms * 4);
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
