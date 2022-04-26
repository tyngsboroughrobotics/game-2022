from lib.libwallaby import libwallaby
from threading import Thread
import sys
import os


def exit_on_enter():
    if input() == "":
        print("Exiting...", flush=True)
        libwallaby.ao()
        libwallaby.disable_servos()
        os._exit(2)


if __name__ == "__main__":
    thread = Thread(target=exit_on_enter)
    thread.start()

    __import__(sys.argv[1]).main()
