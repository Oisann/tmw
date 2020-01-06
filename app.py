#!/usr/bin/env python3

import sys
import os
import json

def hasRepoSetup():
    raw_settings = os.getenv("TMW_SETTINGS_OBJECT", "")
    if len(raw_settings) == 0:
        return False
    settings = json.loads(raw_settings)
    if not settings:
        return False
    # Should probably check if the JSON object is valid...
    return True

def ensureRepo():
    if not hasRepoSetup():
        print(f"Repo is not set up correctly! Please run '{sys.argv[0]} setup'.")
        exit()
    

def main():
    args = sys.argv[1:]
    if args[0]:
        mode = args[0].lower()
        if mode == 'start':
            ensureRepo()
            # Start a new day!
            pass
        elif mode == 'end':
            ensureRepo()
            # End a day!
            pass
        elif mode == 'update':
            ensureRepo()
            # Add an update
            pass
        elif mode == 'setup':
            # Setup a new git repo as a database
            if hasRepoSetup():
                answer = input("You are about to overwrite an older setup. Are you sure about this? y/N: ").lower()
                if answer != "y" and answer != "yes":
                    exit()
            # Setup local path
            location = input("Where can the repo be found on your machine?: ")
            location_abs = os.path.abspath(location)
            answer = input(f"Confirm this path is \"{location_abs}\" - y/N: ").lower()
            if answer != "y" and answer != "yes":
                exit()
            
            # Confirm remote
            remote = input("Set correct git remote (default: origin): ").strip()
            if len(remote) == 0:
                remote = "origin"
            print(f"Using git remote: {remote}")
            settings = {
                "location": location_abs,
                "git": {
                    remote: remote
                }
            }
            output = json.dumps(settings)
            # WHY DOESN'T THIS EXPORT THE VARIABLE????
            os.environ["TMW_SETTINGS_OBJECT"] = output
            print("Settings stored!")

if __name__ == "__main__":
    main()