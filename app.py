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

def getToday(date=""):
    if date != "":
        today = datetime.datetime.strptime(date, "%d.%m.%Y")
        now = today
    else:
        today = datetime.date.today()
        now = datetime.datetime.now()
    fullDate = str(today.strftime("%d.%m.%Y"))
    year = str(today.strftime("%Y"))
    month = str(today.strftime("%m"))
    day = str(today.strftime("%d"))
    timestamp = int((now - datetime.datetime(1970, 1, 1)).total_seconds())
    return {
        "today":today,
        "year": year,
        "month": month,
        "day": day,
        "timestamp": timestamp,
        "fulldate": fullDate
    }

def getDuration(seconds):
    t = str(datetime.timedelta(seconds=seconds)).split(":")
    r = []
    for n in t:
        i = int(n)
        if i < 10:
            r.append(f"0{i}")
        else:
            r.append(str(i))
    return ":".join(r)

def getWorkDurationInSeconds(lines):
    start = -1
    end = -1
    breakTime = 0
    onBreak = -1
    for line in lines:
        l = line.strip().split(" - ")
        if l[1].startswith("Start") and start == -1:
            start = int(l[0])
            continue
        if start == -1:
            continue
        isBreak = l[1].startswith("-")
        if onBreak >= 0:
            if not isBreak:
                breakTime += int(l[0]) - onBreak
                onBreak = -1
        else:
            if isBreak:
                onBreak = int(l[0])
        if l[1].startswith("End") and end == -1:
            end = int(l[0])
            break
    if end == -1:
        end = getToday()["timestamp"]
    return (end - start) - breakTime

def main(args):
    args = args[1:]
    if len(args) > 0:
        mode = args[0].lower()
        mode_args = args[1:]

        if mode == 'break':
            mode = 'update'
            mode_args[0] = f"-{mode_args[0]}"

        if mode == 'start':
            ensureRepo()
            gitPull()
            settings = hasRepoSetup(True)
            today = getToday(" ".join(mode_args))
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
            today = getToday(" ".join(mode_args))
            path = f"{settings['location']}/{today['year']}/{today['month']}"
            filePath = f"{path}/{today['day']}.txt"

            try:
                with open(filePath, 'r+') as file:
                    lines = file.readlines()
                    last = lines[-1]
                    if last.split(" - ")[1].startswith("End"):
                        print(f"{today['fulldate']} has already been ended...")
                        exit()
                    endLine = f"\n{today['timestamp']} - End"
                    file.write(endLine)
                    lines.append(endLine)
                    timeAtWork = getWorkDurationInSeconds(lines)
                    print(f"You spent {getDuration(timeAtWork)} at work on {today['fulldate']}!")
            except FileNotFoundError:
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
                with open(filePath, 'r+') as file:
                    lines = file.readlines()
                    last = lines[-1]
                    if last.split(" - ")[1].startswith("End"):
                        print(f"{today['fulldate']} has already been ended...")
                        exit()
                    endLine = f"\n{today['timestamp']} - {reason}"
                    file.write(endLine)
                    lines.append(endLine)
                    timeAtWork = getWorkDurationInSeconds(lines)
                    print(f"You spent {getDuration(timeAtWork)} at work on {today['fulldate']}!")
            except FileNotFoundError:
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

        elif mode == 'status':
            ensureRepo()
            gitPull()
            settings = hasRepoSetup(True)
            today = getToday(" ".join(mode_args))
            path = f"{settings['location']}/{today['year']}/{today['month']}"
            filePath = f"{path}/{today['day']}.txt"

            lines = []
            try:
                with open(filePath, 'r') as file:
                    lines = file.readlines()
            except FileNotFoundError:
                print(f"You have not started {today['fulldate']} yet!")
                exit()

            s = getWorkDurationInSeconds(lines)
            print(f"You have spent {getDuration(s)} at work on {today['fulldate']}.")
    else:
        main(["", "status"])

if __name__ == "__main__":
    main(sys.argv)