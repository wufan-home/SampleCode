# The script will split one line by blank and fill the words by 
# word1,word2 into the target file.

#!/usr/bin/env python3


import argparse
import datetime
import os
import time


if __name__ == '__main__':
    print("Start format source data file ", datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%dT%H:%M:%S"))

    parser = argparse.ArgumentParser()
    parser.add_argument("-o", dest="output", required=True, help="The path/file to output.")
    parser.add_argument("-f", dest="filename", required=True, help="The path/file to rack list")
    args = parser.parse_args()

    if not os.path.exists(args.filename):
        print('File {} does not exist.'.format(args.filename))
        exit(1)

    if os.path.exists(args.output):
        print('The output file {} exist. Remove it'.format(args.output))
        os.remove(args.output)

    with open(args.filename) as reader:
        lines = reader.readlines()

    with open(args.output, 'w') as writer:
        for line in lines:
            words = line.split()
            for i in range(0, len(words), 2):
                writer.write('{},{}\n'.format(words[i], words[i + 1]))

    print("End format source data file ", datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%dT%H:%M:%S"))
