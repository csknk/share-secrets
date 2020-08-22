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
    def __init__(self, shares_list, label=''):
        self.shares_list = shares_list
        self.label = label
        self.report = ''
        self.base_dir = ''
        self.load_config()
        self.set_base_dir()
        self.save_to_files()
        self.clean_up()

    def load_config(self):
        with open('config.json') as f:
            self.config = json.load(f)

    def set_base_dir(self):
        cmd = [
            'zenity',
            '--file-selection',
            '--directory',
            '--title=_select the directory in which to save shares.'
            ]
        try:
            self.base_dir = subprocess.check_output(cmd).decode('utf-8').strip()
            print("base_dir set: {}".format(self.base_dir))
        except subprocess._called_process_error as e:
            print(e.output)

    # Output fragments to files
    def save_to_files(self):
        self.dir = self.base_dir + '/shared-secrets-' + str(int(time.time()))
        pathlib.Path(self.dir).mkdir(parents=True, exist_ok=True, mode=0o755)
        self.create_readme(self.dir)

        for index, fragment in enumerate(self.shares_list):
            filepath = "{dir}/{rootname}-{label}-{index}".format(
                dir=self.dir,
                rootname=self.config['fragments']['filenameRoot'],
                label=self.label,
                index=str(index + 1)
            )
            self.create_file_markdown(fragment=fragment, filepath=filepath)
            self.create_file_pdf(fragment=fragment, filepath=filepath)
            self.create_file_html(fragment=fragment, filepath=filepath)

    def create_file_markdown(self, **kwargs):
        if kwargs:
            fragment = kwargs["fragment"]
            filepath = kwargs["filepath"]
        d = {
        'label': self.label,
        'timestamp': datetime.datetime.now().strftime("%d-%b-%Y %H:%M:%S"),
        'report': self.report,
        'contact_name': self.config['contact']['name'],
        'contact_email': self.config['contact']['email'],
        'fragment': fragment
        }
        filein = open('text/fragment.md')
        src = Template(filein.read())
        content = src.substitute(d)
        file = open(filepath + ".md", 'w')
        file.write(content)
        file.close()

    # _output fragments to _p_d_f files
    def create_file_html(self, **kwargs):
        if kwargs:
            fragment = kwargs["fragment"]
            filepath = kwargs["filepath"]

        html_content = {
            'label': self.label,
            'timestamp': datetime.datetime.now().strftime("%d-%b-%Y %H:%M:%S"),
            'report': self.report,
            'contact_name': self.config['contact']['name'],
            'contact_email': self.config['contact']['email'],
            'fragment': fragment,
            'img_src': filepath + ".png"
        }
        filein = open('text/fragment-basic.html')
        src = Template(filein.read())
        file = open(filepath + ".html", 'w')
        file.write(src.substitute(html_content))
        file.close()

    # Output fragments to pdf files
    def create_file_pdf(self, **kwargs):
        if kwargs:
            fragment = kwargs["fragment"]
            filepath = kwargs["filepath"]

        qr_image_file = self.make_qr_code(fragment);
        qr_image_file.save("{}{}".format(filepath, ".png"))
        html_content = {
            'label': self.label,
            'timestamp': datetime.datetime.now().strftime("%d-%b-%Y %H:%M:%S"),
            'report': self.report,
            'contact_name': self.config['contact']['name'],
            'contact_email': self.config['contact']['email'],
            'fragment': fragment,
            'img_src': filepath + ".png"
        }
        html_file_in = open('text/fragment.html')
        html_src = Template(html_file_in.read())
        html_fragment = html_src.substitute(html_content)
        pdf = pydf.generate_pdf(html_fragment, image_quality=100, image_dpi=1000)
        with open(filepath + ".pdf", 'wb') as f:
            f.write(pdf)

    def make_qr_code(self, fragment):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(fragment)
        qr.make(fit=True)
        return qr.make_image(fill_color="black", back_color="white")

    def create_readme(self, dir):
        d = {
        'label': self.label,
        'timestamp': datetime.datetime.now().strftime("%d-%b-%Y %H:%M:%S")
        }
        filein = open('text/readme.txt')
        src = Template(filein.read())
        readme_content = src.substitute(d)
        readme = dir + '/README.md'
        file = open(readme, 'w')
        file.write(textwrap.dedent(readme_content))
        file.close()

    def clean_up(self):
        print("Your secrets have been split and saved as individual files. Holding these files in one place is a security vulnerability.")
        print("Files:")
        pathlist = Path(self.dir).glob('**/*')
        for path in pathlist:
            print(path)
        if click.confirm("Do you want to securely shred the files?", default=True):
            pathlist = Path(self.dir).glob('**/*.txt')
            for index, path in enumerate(pathlist):
                print("_shredding {}...".format(str(path)))
                cmd = ['shred', '-vfzu', str(path)]
                stdoutdata = subprocess.check_output(cmd).decode('utf-8')
                print("stdoutdata: " + stdoutdata)
