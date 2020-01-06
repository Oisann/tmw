#!/usr/bin/env python3

import os
import sys
import json
import datetime
import subprocess

def hasRepoSetup(s = False):
    raw_settings = os.getenv("TMW_SETTINGS_OBJECT", "")
    if len(raw_settings) == 0:
        return False
    settings = json.loads(raw_settings)
    if not settings:
        return False
    # Should probably check if the JSON object is valid...
    if s:
        return settings
    return True

def ensureRepo():
    if not hasRepoSetup():
        print(f"Repo is not set up correctly! Please run '{sys.argv[0]} setup'.")
        exit()

def gitPull():
    settings = hasRepoSetup(True)
    pull = subprocess.run(['git','pull'], cwd=settings["location"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    result = pull.stdout
    result = f"{result}\n{pull.stderr}"
    if "Already up to date." in result:
        return ""
    return result.strip()

def gitCommit(message, file = '.'):
    settings = hasRepoSetup(True)
    gitAdd = subprocess.run(['git','add', file, '-v'], cwd=settings["location"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    result = gitAdd.stdout
    result = f"{result}\n{gitAdd.stderr}"
    if len(result.strip()) == 0:
        return ""
    gitCommit = subprocess.run(['git','commit', '-m', f"{message}"], cwd=settings["location"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    result = f"{result}\n{gitCommit.stdout}"
    result = f"{result}\n{gitCommit.stderr}"
    return result.strip()

def gitPush():
    settings = hasRepoSetup(True)
    push = subprocess.run(['git','push', settings["git"]["remote"], settings["git"]["branch"]], cwd=settings["location"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    result = push.stdout
    result = f"{result}\n{push.stderr}"
    if "Everything up-to-date" in result:
        return ""
    return result.strip()

def getToday():
    today = datetime.date.today()
    fullDate = str(today.strftime("%d.%m.%Y"))
    year = str(today.strftime("%Y"))
    month = str(today.strftime("%m"))
    day = str(today.strftime("%d"))
    timestamp = int((datetime.datetime.now() - datetime.datetime(1970, 1, 1)).total_seconds())
    return {
        "today":today,
        "year": year,
        "month": month,
        "day": day,
        "timestamp": timestamp,
        "fulldate": fullDate
    }

def main():
    args = sys.argv[1:]
    if args[0]:
        mode = args[0].lower()
        mode_args = args[1:]
        if mode == 'start':
            ensureRepo()
            gitPull()
            settings = hasRepoSetup(True)
            today = getToday()
            path = f"{settings['location']}/{today['year']}/{today['month']}"
            filePath = f"{path}/{today['day']}.txt"
            os.makedirs(path, exist_ok=True)

            try:
                with open(filePath, 'r'):
                    print(f"You have already started {today['fulldate']}!")
                exit()
            except FileNotFoundError:
                # TODO: Check if the previous day (work day, aka try to find the last file?) has ended. Maybe we forgot to end it...
                with open(filePath, 'w') as file:
                    file.write(f"{today['timestamp']} - Start")
            gitCommit(f"Started {today['fulldate']}")
            gitPush()
            print(f"Started {today['fulldate']}")

        elif mode == 'end':
            ensureRepo()
            gitPull()
            settings = hasRepoSetup(True)
            today = getToday()
            path = f"{settings['location']}/{today['year']}/{today['month']}"
            filePath = f"{path}/{today['day']}.txt"

            try:
                with open(filePath, 'a+') as file:
                    #lines = file.readlines()
                    #print(lines, filePath)
                    #last = lines[-1]
                    #if last.split(" - ")[1] == "End":
                    #    print(f"{today['fulldate']} has already been ended...")
                    file.write(f"{today['timestamp']} - End")
                    #for line in lines:
                    #    p = line.split(" - ")
                    #    if p[1] == "Start":
                    #        # TODO: Add a way to remove breaks inbetween start and end.
                    #        t = int(p[0])
                    #        n = int(today['timestamp'])
                    #        e = n - t
                    #        duration = str(datetime.timedelta(seconds=e))
                    #        print(f"You spent {duration} at work today.")
                    #        break
            except FileNotFoundError:
                with open(filePath, 'r'):
                    print(f"You have not started {today['fulldate']} yet!")
                exit()
                
            gitCommit(f"Ended {today['fulldate']}")
            gitPush()
            print(f"Ended {today['fulldate']}")

        elif mode == 'update':
            ensureRepo()
            if len(mode_args) == 0:
                print("ERROR: You need to enter a reason when updating the log.")
                exit()
            reason = " ".join(mode_args)
            gitPull()
            settings = hasRepoSetup(True)
            today = getToday()
            path = f"{settings['location']}/{today['year']}/{today['month']}"
            filePath = f"{path}/{today['day']}.txt"

            try:
                with open(filePath, 'a') as file:
                    file.write(f"{today['timestamp']} - {reason}")
            except FileNotFoundError:
                with open(filePath, 'r'):
                    print(f"You have not started {today['fulldate']} yet!")
                exit()

            gitCommit(f"Updated {today['fulldate']}")
            gitPush()
            print(f"Updated {today['fulldate']}")

        elif mode == 'setup':
            # Setup a new git repo as a database
            if hasRepoSetup():
                print("NOTE: You already have TMW set up!")
            # Setup local path
            location = input("Where can the repo be found on your machine?: ")
            location_abs = os.path.abspath(location)
            answer = input(f"Confirm this path is \"{location_abs}\" - y/N: ").lower().strip()
            if answer != "y" and answer != "yes":
                exit()
            
            # Confirm remote
            remote = input("Set correct git remote (default: origin): ").strip()
            if len(remote) == 0:
                remote = "origin"
            print(f"Using git remote: {remote}")

            # Confirm branch
            branch = input("Set correct git branch (default: master): ").strip()
            if len(branch) == 0:
                branch = "master"
            print(f"Using git branch: {branch}")

            settings = {
                "location": location_abs,
                "git": {
                    "remote": remote,
                    "branch": branch
                }
            }
            output = json.dumps(settings)
            print("Save the settings by running this command:")
            print("")
            print(f"export TMW_SETTINGS_OBJECT='{output}'")
            print("")

if __name__ == "__main__":
    main()