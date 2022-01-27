#if __has_include(<kipr/wombat.h>)
#include <kipr/wombat.h>
#else
#error "Please compile on the Wombat"
#endif

#include <stdio.h>
#include <stdlib.h>
#include "wheels.h"

const int red_channel = 0;
const int green_channel = 1;

const Servo plow_servo = {
    .port = 0,
};

const Motor plow_winch = {
    .port = 2,
    .speed = 1.0,
};

const Wheels wheels = {
    .left_motor = {
        .port = 0,
        .speed = 0.5, //1.0,
    },
    .right_motor = {
        .port = 1,
        .speed = 0.5, //1.0,
    },
    .left_offset = 1.25,
    .right_offset = 1.0,
};

void collect_pom(TurnDirection direction);
void raise_plow();
void lower_plow();
void open_plow();
void close_plow();

int main() {
    camera_open();

    raise_plow();
    open_plow();
    lower_plow();

    for (int i = 0; i < 1; i++) {
        for (int i = 0; i < 10; i++) {
            camera_update();
        }

        if (get_object_count(red_channel) > 0) {
            // Red pom
            printf("Red!\n"); fflush(stdout);
            collect_pom(LEFT);
        } else {
            // Green pom
            printf("Green!\n"); fflush(stdout);
            collect_pom(RIGHT);
        }

        drive_wheels(wheels, FORWARD, IN(6));

        msleep(2000); // TODO: TEMPORARY
    }

    close_plow();
    raise_plow();

    camera_close();

    return 0;
}

void collect_pom(TurnDirection direction) {
    const double turn_amount = 30.0;
    const double drive_amount = CM(10.0);

    // Turn to collect the poms
    turn_wheels(wheels, direction, turn_amount);
    drive_wheels(wheels, FORWARD, drive_amount);

    // Get back on track
    turn_wheels(wheels, !direction, turn_amount * 2);
    drive_wheels(wheels, FORWARD, drive_amount);
    turn_wheels(wheels, direction, turn_amount);
}

const int plow_open_amount = CM(100);
const int plow_raised_position = 750;
const int plow_lowered_position = 1055;

void raise_plow() {
    set_servo(plow_servo, plow_raised_position);
}

void lower_plow() {
    set_servo(plow_servo, plow_lowered_position);
}

void open_plow() {
    drive_motor(plow_winch, FORWARD, plow_open_amount);
}

void close_plow() {
    drive_motor(plow_winch, REVERSE, plow_open_amount);
}
