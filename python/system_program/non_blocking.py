# This is a sample of non-blocking call written by Python.
# This approach is a classical: it uses yield (similar as goto in C/C++/Java) to set up 
# a jump from the place where the output has to be waited.
# The output has to be generated in the asynchronized way: In this sample code, we uses subprocess.open and poll.

