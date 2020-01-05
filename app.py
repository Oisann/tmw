#!/usr/bin/env python3

import sys

def main():
    args = sys.argv[1:]
    if args[1]:
        mode = args[1].lower()
        if mode == 'start':
            # Start a new day!
            pass
        elif mode == 'end':
            # End a day!
            pass
        elif mode == 'update':
            # Add an update
            pass
        elif mode == 'setup':
            # Setup a new git repo as a database
            pass

if __name__ == "__main__":
    main()