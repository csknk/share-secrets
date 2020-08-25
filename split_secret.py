import pathlib
import subprocess
from create_files import CreateFiles


class SplitSecret:
    """Collects data from user and splits a secret into shares.
    
    Requires the ssss debian package which perfoms the actual splitting by means of
    Shamir's Secret Sharing Scheme.

    The secret is split into n_shares, of which n_required are needed to recreate the secret.
    """
    def __init__(self):
        self.n_shares = 0
        self.n_required = 0

    def run(self):
        self.get_user_data()
        self.run_cmd()
        self.output()

    def get_user_data(self):
        """Get user data interactively.
        
        Sets n_shares, n_required and the label.
        """
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

    def create_shares_list(self):
        """Make a list of shares."""
        result = []
        for row in self.returned_output.decode('utf-8').split('\n'):
            result.append(row.lstrip())
        
        # Filter the last element, which is empty
        result = list(filter(None, result))
        self.report = result[0]
        
        # Exclude the first element, which is the report
        self.shares_list = result[1:]

    def output(self):
        """Output to terminal."""
        print("\n{}\n{}".format(self.report, (u'\u2014' * 80)))
        for fragment in self.shares_list:
            print(fragment)
        print(u'\u2014' * 80)

    def __str__(self):
        return "%s required from %s fragments, labelled %s." % (
            self.n_required, self.n_shares, self.label)
