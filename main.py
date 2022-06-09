#!/usr/bin/env python3
from server import SimpleEchoServer


def main():
    """Connect to the server with `telnet $HOSTNAME 5000`."""
    server = SimpleEchoServer()
    server.run()


if __name__ == "__main__":
    main()
