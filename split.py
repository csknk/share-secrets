#!/usr/bin/python3
import subprocess, sys, getopt
from SplitSecret import SplitSecret

def main():

    s = SplitSecret()
    s.run()

if __name__ == '__main__':
    main()
