#include <kipr/wombat.h>

// Function Signitures 
void out_box();
void drive(double l_seconds, double r_seconds);

const int basket = 0;

int main() {
    printf("Starting Up...\n");
    create_connect();
    motor(basket, -100);
    msleep(1000);
    ao();
    //out_box();
    create_disconnect();
}

/*void out_box(){
// msleep(5000);
    drive()
    msleep(2400);
    create_stop();
    create_disconnect();
}

void drive(double l_seconds, double r_seconds){
    create_drive_direct(l_seconds*1000, r_seconds*1000);
}
*/