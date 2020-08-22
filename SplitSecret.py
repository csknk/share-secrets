#!/usr/bin/python3
import pathlib
import subprocess
from CreateFiles import CreateFiles


class SplitSecret:
    def __init__(self):
        self.n_shares = 0
        self.n_required = 0

    def run(self):
        self.get_user_data()
        self.run_cmd()
        self.output()

    def get_user_data(self):
        self.n_shares = input("Enter the required number of shares:")
        self.n_required = input(
            "Enter the number of shares necessary to rebuild the secret:")
        self.label = input("Enter a one-word label for the share fragments:")

    def run_cmd(self):
        n_required = '-t ' + self.n_required
        n_shares = '-n ' + self.n_shares
        label = '-w ' + self.label
        cmd = ['ssss-split', n_shares, n_required, label]
        self.returned_output = subprocess.check_output(cmd)
        self.create_shares_list()

    # Make a list of shares
    def create_shares_list(self):
        result = []
        for row in self.returned_output.decode('utf-8').split('\n'):
            result.append(row.lstrip())
        # Filter the last element, which is empty
        result = list(filter(None, result))
        self.report = result[0]
        # Exclude the first element, which is the report
        self.shares_list = result[1:]

    # Output to terminal function
    def output(self):
        print("\n{}\n{}".format(self.report, (u'\u2014' * 80)))
        for fragment in self.shares_list:
            print(fragment)
        print(u'\u2014' * 80)

    def __str__(self):
        return "%s required from %s fragments, labelled %s." % (
            self.n_required, self.n_shares, self.label)
