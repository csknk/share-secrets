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
import pydf

class CreateFiles():
    def __init__(self, sharesList, label=''):
        self.sharesList = sharesList
        self.label = label
        self.report = ''
        self.baseDir = ''
        self.loadConfig()
        self.setBaseDir()
        self.saveToFiles()
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

        for index, fragment in enumerate(self.sharesList):
            filepath = "{dir}/{rootname}-{label}-{index}".format(
                dir=self.dir,
                rootname=self.config['fragments']['filenameRoot'],
                label=self.label,
                index=str(index + 1)
            )
            self.createFileMarkdown(fragment=fragment, filepath=filepath)
            self.createFilePDF(fragment=fragment, filepath=filepath)
            self.createFileHTML(fragment=fragment, filepath=filepath)

    def createFileMarkdown(self, **kwargs):
        if kwargs:
            fragment = kwargs["fragment"]
            filepath = kwargs["filepath"]
        d = {
        'label': self.label,
        'timestamp': datetime.datetime.now().strftime("%d-%b-%Y %H:%M:%S"),
        'report': self.report,
        'contactName': self.config['contact']['name'],
        'contactEmail': self.config['contact']['email'],
        'fragment': fragment
        }
        filein = open('text/fragment.md')
        src = Template(filein.read())
        content = src.substitute(d)
        file = open(filepath + ".md", 'w')
        file.write(content)
        file.close()

    # Output fragments to PDF files
    def createFileHTML(self, **kwargs):
        if kwargs:
            fragment = kwargs["fragment"]
            filepath = kwargs["filepath"]

        HTMLContent = {
            'label': self.label,
            'timestamp': datetime.datetime.now().strftime("%d-%b-%Y %H:%M:%S"),
            'report': self.report,
            'contactName': self.config['contact']['name'],
            'contactEmail': self.config['contact']['email'],
            'fragment': fragment,
            'imgSrc': filepath + ".png"
        }
        filein = open('text/fragment-basic.html')
        src = Template(filein.read())
        file = open(filepath + ".html", 'w')
        file.write(src.substitute(HTMLContent))
        file.close()

    # Output fragments to PDF files
    def createFilePDF(self, **kwargs):
        if kwargs:
            fragment = kwargs["fragment"]
            filepath = kwargs["filepath"]

        qrImageFile = self.makeQRCode(fragment);
        qrImageFile.save("{}{}".format(filepath, ".png"))
        HTMLContent = {
            'label': self.label,
            'timestamp': datetime.datetime.now().strftime("%d-%b-%Y %H:%M:%S"),
            'report': self.report,
            'contactName': self.config['contact']['name'],
            'contactEmail': self.config['contact']['email'],
            'fragment': fragment,
            'imgSrc': filepath + ".png"
        }
        HTMLfilein = open('text/fragment.html')
        HTMLsrc = Template(HTMLfilein.read())
        HTMLfragment = HTMLsrc.substitute(HTMLContent)
        pdf = pydf.generate_pdf(HTMLfragment, image_quality=100, image_dpi=1000)
        with open(filepath + ".pdf", 'wb') as f:
            f.write(pdf)

    def makeQRCode(self, fragment):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(fragment)
        qr.make(fit=True)
        return qr.make_image(fill_color="black", back_color="white")

    def createReadme(self, dir):
        d = {
        'label': self.label,
        'timestamp': datetime.datetime.now().strftime("%d-%b-%Y %H:%M:%S")
        }
        filein = open('text/readme.txt')
        src = Template(filein.read())
        readmeContent = src.substitute(d)
        readme = dir + '/README.md'
        file = open(readme, 'w')
        file.write(textwrap.dedent(readmeContent))
        file.close()

    def cleanUp(self):
        print("Your secrets have been split and saved as individual files. Holding these files in one place may be a security vulnerability.")
        print("Files:")
        pathlist = Path(self.dir).glob('**/*')
        for path in pathlist:
            print(path)
        if click.confirm("Do you want to securely shred the files?", default=True):
            pathlist = Path(self.dir).glob('**/*.txt')
            for index, path in enumerate(pathlist):
                print("Shredding {}...".format(str(path)))
                cmd = ['shred', '-vfzu', str(path)]
                stdoutdata = subprocess.check_output(cmd).decode('utf-8')
                print("stdoutdata: " + stdoutdata)
