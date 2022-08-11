#!/usr/bin/python

## Tnput: a string '' or "".
## Output: A list of lines from the output.

import subprocess


# This is the preferred approach.
# The call of this function is blocking.
# cmd can be a string or an array.
def execute_linux_command(cmd, log_file):
    # To avoid infinity loops, any command can only be executed for 120 seconds.
    try:
        response = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                  encoding="utf-8", timeout=120)
    except subprocess.TimeoutExpired:
        log(log_file, "ERROR", "Timeout of the command: " + cmd)
        return None
    if response is None:
        log(log_file, "ERROR", "Failed to get the output the command: " + cmd)
        return None
    log(log_file, "INFO", "Successfully run the command: " + cmd)
    return response


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
