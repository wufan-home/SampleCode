import argparse
import os
import subprocess
import datetime
import time

def execute(cmd, times, interval_sec):
    for i in range(int(times)):
        subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        print datetime.datetime.now().strftime("%Y-%m-%dT%I:%M:%S%p"), ": [", i , "/" , times ,"] ", cmd
        time.sleep(int(interval_sec))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--command", required=True,
                        help="The command to be executed")
    parser.add_argument("-t", "--times", required=True,
                        help="The repeat times of executing the command")
    parser.add_argument("-i", "--interval", required=True,
                        help="The interval between two times of execution")
    args = parser.parse_args()
    execute(args.command, args.times, args.interval)
