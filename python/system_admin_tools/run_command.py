#!/usr/bin/python

## Tnput: a string '' or "".
## Output: A list of lines from the output.

import subprocess


# This is the preferred approach.
# The call of this function is blocking.
# cmd can be a string or an array.
# use_shell: use the shell to parse the cmd_array. This is for the locally running command. 
# Default: True.
# timeout_s: timeout in second. Default is 5 seconds.
def run(cmd_array, use_shell=True, timeout_s=5, log_file):
    # To avoid infinity loops, any command can only be executed for 120 seconds.
    try:
        response = subprocess.run(cmd_array, shell=use_shell, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                  encoding="utf-8", timeout=timeout_s)
    except subprocess.TimeoutExpired:
        log.write("ERROR", "Timeout (" + str(timeout_s) + " seconds): " + ' '.join(cmd_array))
        return None
    except subprocess.CalledProcessError:
        log.write('ERROR', 'Server Error: ' + ' '.join(cmd_array))
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
