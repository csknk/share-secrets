#!/usr/bin/python3
import pathlib
import json
import subprocess
import datetime
import time
import textwrap
import click
from string import Template
from pathlib import Path

class SplitSecret:
    def __init__(self):
        self.nShares = 0
        self.nRequired = 0
        self.label = ''
        self.report = ''
        self.baseDir = ''
        self.loadConfig()
        self.shredReport = {}
        self.setBaseDir()
        self.getUserData()

    def run(self):
        self.runCmd()
        self.output()
        self.saveToFiles()
        self.cleanUp()

    def setBaseDir(self):
        cmd = [
            'zenity',
            '--file-selection',
            '--directory',
            '--title=Select the directory in which to save shares.'
            ]
        try:
            self.baseDir = subprocess.check_output(cmd).decode('utf-8').strip()
            print("baseDir set: {}".format(self.baseDir))
        except subprocess.CalledProcessError as e:
            print(e.output)

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

    # Output fragments to files
    def saveToFiles(self):
        self.dir = self.baseDir + '/shared-secrets-' + str(int(time.time()))
        pathlib.Path(self.dir).mkdir(parents=True, exist_ok=True, mode=0o755)
        self.createReadme(self.dir)

        d = {
        'label': self.label,
        'timestamp': datetime.datetime.now().strftime("%d-%b-%Y %H:%M:%S"),
        'report': self.report,
        'contactName': self.config['contact']['name'],
        'contactEmail': self.config['contact']['email']
        }
        filein = open('text/fragment_header.txt')
        src = Template(filein.read())
        fragmentHeaderContent = src.substitute(d)

        for index, fragment in enumerate(self.sharesList):
            filepath = "{dir}/{rootname}-{label}-{index}.txt".format(
                dir=self.dir,
                rootname=self.config['fragments']['filenameRoot'],
                label=self.label,
                index=str(index + 1)
            )
            file = open(filepath, 'w')
            file.write(fragmentHeaderContent)
            file.write(fragment + '\n')
            file.close()

    def createReadme(self, dir):
        d = {
        'label': self.label,
        'timestamp': datetime.datetime.now().strftime("%d-%b-%Y %H:%M:%S")
        }
        filein = open('text/readme.txt')
        src = Template(filein.read())
        readmeContent = src.substitute(d)
        readme = dir + '/readme.md'
        file = open(readme, 'w')
        file.write(textwrap.dedent(readmeContent))
        file.close()

    def loadConfig(self):
        with open('config.json') as f:
            self.config = json.load(f)

    def cleanUp(self):
        print("Your secrets have been split and saved as individual files. Holding these files in one place may be a security vulnerability.")
        print("Files:")
        pathlist = Path(self.dir).glob('**/*.txt')
        for path in pathlist:
            print(path)
        if click.confirm("Do you want to securely shred the files?", default=True):
            pathlist = Path(self.dir).glob('**/*.txt')
            for index, path in enumerate(pathlist):
                print("Shredding {}...".format(str(path)))
                cmd = ['shred', '-vfzu', str(path)]
                stdoutdata = subprocess.check_output(cmd).decode('utf-8')
                print("stdoutdata: " + stdoutdata)

    def __str__(self):
        return "%s required from %s fragments, labelled %s." % (self.nRequired, self.nShares, self.label)
