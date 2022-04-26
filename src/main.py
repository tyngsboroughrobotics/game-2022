import sys

if __name__ == "__main__":
    try:
        __import__(sys.argv[1]).main()
    except KeyboardInterrupt:
        sys.exit(0)
