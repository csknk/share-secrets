#!/usr/bin/env python3
import subprocess
import sys
import getopt
from split_secret import SplitSecret
from create_files import CreateFiles


def main():

    s = SplitSecret()
    s.run()
    CreateFiles(s.shares_list, s.label)


if __name__ == '__main__':
    main()
