#if __has_include(<kipr/wombat.h>)
#include <kipr/wombat.h>
#else
#error "Please compile on the Wombat"
#endif

#include <stdio.h>
#include <stdlib.h>

// Signatures
void out_box();
void drive(int l_velocity, int r_velocity, int duration);
void open_basket_full();
void close_basket_full();
void open_basket_partway();
void close_basket_partway();
void move_motor(int port, int velocity, int duration);
void turn_l(int degrees);
void turn_r(int degrees);

// Variables
const int basket = 0;
const int basket_full_open_duration = 8000;
const int basket_partway_duration = 2000;
const double ticks_per_degree = 4.25;

int main() {
   printf("Starting Up...\n");
   create_connect();
   out_box();
   create_disconnect();

   return 0;
}

void out_box(){
    int start_wait_time = 3000;
    int time_to_cross = 900;

    open_basket_partway();
    msleep(start_wait_time);
    drive(1000, 1000, time_to_cross);
    turn_r(90);
    drive(1000, 1000, 1400);
    turn_l(95);
    drive(1000, 1000, 300);
    close_basket_partway();
    create_disconnect();
}

void drive(int l_velocity, int r_velocity, int duration){
   create_drive_direct(l_velocity, r_velocity);
   msleep(duration);
   create_stop();
}

void open_basket_full(){
    move_motor(basket, -100, basket_full_open_duration);
}
void close_basket_full(){
    move_motor(basket, 100, basket_full_open_duration);
}

void open_basket_partway(){
    move_motor(basket, -100, basket_partway_duration);
}
void close_basket_partway(){
    move_motor(basket, 100, basket_partway_duration);
}

void move_motor(int port, int velocity, int duration){
    motor(port, velocity);
    msleep(duration);
    ao();
}

void turn_l(int degrees){
    drive(-1000, 1000, (int) (degrees * ticks_per_degree));
}

void turn_r(int degrees){
    drive(1000, -1000, (int) (degrees * ticks_per_degree));
}
