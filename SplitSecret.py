#!/usr/bin/python3
import pathlib
import subprocess
from CreateFiles import CreateFiles

class SplitSecret:
    def __init__(self):
        self.nShares = 0
        self.nRequired = 0

    def run(self):
        self.getUserData()
        self.runCmd()
        self.output()

    def getUserData(self):
        self.nShares = input("Enter the required number of shares:")
        self.nRequired = input("Enter the number of shares necessary to rebuild the secret:")
        self.label = input("Enter a one-word label for the share fragments:")

    def runCmd(self):
        nRequired = '-t ' + self.nRequired
        nShares = '-n ' + self.nShares
        label = '-w ' + self.label
        cmd = ['ssss-split', nShares, nRequired, label]
        self.returned_output = subprocess.check_output(cmd)
        self.createSharesList()

    # Make a list of shares
    def createSharesList(self):
        result = []
        for row in self.returned_output.decode('utf-8').split('\n'):
            result.append(row.lstrip())
        # Filter the last element, which is empty
        result = list(filter(None, result))
        self.report = result[0]
        # Exclude the first element, which is the report
        self.sharesList = result[1:]

    # Output to terminal function
    def output(self):
        print("\n{}\n{}".format(self.report, (u'\u2014' * 80)))
        for fragment in self.sharesList:
            print(fragment)
        print(u'\u2014' * 80)

    def __str__(self):
        return "%s required from %s fragments, labelled %s." % (self.nRequired, self.nShares, self.label)
