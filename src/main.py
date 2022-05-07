from lib.libwallaby import libwallaby
from threading import Thread, Timer
import sys
import os


def exit():
    libwallaby.ao()
    libwallaby.disable_servos()
    libwallaby.camera_close()
    os._exit(2)


def exit_on_enter():
    print("Press Enter to exit")
    input()
    print("Exiting...")
    exit()


def wait_for_light():
    port = 0
    threshold = 70

    ambient = libwallaby.analog(port)
    while ambient - libwallaby.analog(port) < threshold:
        print("\rLight:", ambient - libwallaby.analog(port), end="")
        pass

    print()


if __name__ == "__main__":
    thread = Thread(target=exit_on_enter)
    thread.start()

    wait_for_light()

    timer = Timer(119, exit)
    timer.start()

    __import__(sys.argv[1]).main()
    exit()
