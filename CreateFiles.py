#!/usr/bin/python3
import pathlib
from pathlib import Path
import subprocess
import datetime
import time
import json
from string import Template
import textwrap
import click
import qrcode

class CreateFiles():
    def __init__(self, sharesList, label=''):
        self.sharesList = sharesList
        self.label = label
        self.report = ''
        self.baseDir = ''
        self.loadConfig()
        self.setBaseDir()
        self.saveToFiles()
        self.makeQRCodes()
        self.cleanUp()

    def loadConfig(self):
        with open('config.json') as f:
            self.config = json.load(f)

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
            # results/shared-secrets-1534005473/DE--5.txt
            file = open(filepath, 'w')
            file.write(fragmentHeaderContent)
            file.write(fragment + '\n')
            file.close()

    def makeQRCodes(self):
        for index, fragment in enumerate(self.sharesList):
            filepath = "{dir}/{rootname}-{label}-{index}.png".format(
                dir=self.dir,
                rootname=self.config['fragments']['filenameRoot'],
                label=self.label,
                index=str(index + 1)
            )
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(fragment)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            img.save(filepath)

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
