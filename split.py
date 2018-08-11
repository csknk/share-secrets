#!/usr/bin/python3
import subprocess, sys, getopt
from SplitSecret import SplitSecret
from CreateFiles import CreateFiles

def main():

    s = SplitSecret()
    s.run()
    CreateFiles(s.sharesList, s.label)

if __name__ == '__main__':
    main()
