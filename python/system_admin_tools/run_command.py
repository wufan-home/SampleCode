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


## This function accepts the command in the array format,
## like ['ssh', '-i', key, primary_ms_hostname, 'curl',
##       '-H', '\"Content-Type:', 'application/json\"', '-X', 'POST', '-d', json_block,
##       'http://localhost:19000/<api>']
def execute_command_array(cmd_arr):
    output = Popen(cmd_arr, stdout=PIPE).communicate()[0]
    if output is None:
        return None
    return output
