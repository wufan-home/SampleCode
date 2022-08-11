#!/usr/bin/python

## Tnput: a string '' or "".
## Output: A list of lines from the output.

import subprocess


# This is the preferred approach.
# The call of this function is blocking.
# cmd can be a string or an array.
# Why need `shell=True`???
def run(cmd_array, use_shell, timeout_s, log_file):
    # To avoid infinity loops, any command can only be executed for 120 seconds.
    try:
        response = subprocess.run(cmd_array, shell=use_shell, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                  encoding="utf-8", timeout=timeout_s)
    except subprocess.TimeoutExpired:
        log.write("ERROR", "Timeout: " + ' '.join(cmd_array))
        return None
    if response is None:
        log.write("ERROR", "None output: " + ' '.join(cmd_array))
    else:
        log.write("INFO", "Success: " + ' '.join(cmd_array))
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
