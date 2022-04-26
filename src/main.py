from lib.libwallaby import libwallaby
from threading import Thread
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
    print("Exiting...", flush=True)
    exit()


if __name__ == "__main__":
    thread = Thread(target=exit_on_enter)
    thread.start()

    __import__(sys.argv[1]).main()
    exit()
