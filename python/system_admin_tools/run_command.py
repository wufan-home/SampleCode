#!/usr/bin/python

## Tnput: a string '' or "".
## Output: A list of lines from the output.

import subprocess


def run_command(cmd):
    raw_output = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    if raw_output is None:
        return None
    output = raw_output.stdout.readlines()
    return output
