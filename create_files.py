import pathlib
from pathlib import Path
import os
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
        """Load config data

        Config data in config.json should include the following fields:

        {
          "contact": {
            "name": "Joe Bloggs",
            "email": "joe@example.com"
          },
          "fragments": {
            "filenameRoot": "JB-secret"
          }
        }
        """
        with open('config.json') as f:
            self.config = json.load(f)

    def set_base_dir(self):
        """Obtain the base directory from user input.
        Default directory is /tmp
        """
        while 1:
            msg = "Please enter a path: blank defaults to /tmp: "
            path = Path(input(msg) or "/tmp").expanduser()
            if path.is_dir() and os.access(path, os.W_OK):
                break
            print("Invalid path or you do not have write access at that location...")
        self.base_dir = path
    
    def set_base_dir_graphical(self):
        """Probably deprecated."""
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

    def save_to_files(self):
        """
        Setup directory structure and control file creation for each fragment in the shares_list.
        
        Loop through the shares_list and create markdown, HTML & PDF files for each.
        """
        subdir = "shared-secrets-" + str(int(time.time()))
        self.dir = self.base_dir / subdir
        pathlib.Path(self.dir).mkdir(parents=True, exist_ok=True, mode=0o755)
        for subdir in ["html", "md", "pdf", "images"]:
            pathlib.Path(self.dir / subdir).mkdir(parents=True, exist_ok=True, mode=0o755)
        self.create_readme(self.dir)

        for index, fragment in enumerate(self.shares_list):
            filename = "{rootname}-{label}-{index}".format(
                rootname=self.config['fragments']['filenameRoot'],
                label=self.label,
                index=str(index + 1)
            )
            self.create_file(fragment=fragment, dirpath=self.dir, filename=filename, filetype="html")
            self.create_file(fragment=fragment, dirpath=self.dir, filename=filename, filetype="md")
            self.create_file(fragment=fragment, dirpath=self.dir, filename=filename, filetype="pdf")

    def write_file(self, filepath, content):
        """Write content into file specified by filepath.""" 
        file = open(filepath, 'w')
        file.write(content)
        file.close()
 
    def create_file(self, filetype, **kwargs):
        """Create markdown, HTML and PDF files.
        
        Note that PDF requires a HTML input.
        """
        if kwargs:
            fragment = kwargs["fragment"]
            dirpath = kwargs["dirpath"]
            filename = kwargs["filename"]
        
        generic_filename = "{dirpath}/{filetype}/{filename}".format(
                dirpath=dirpath,
                filetype=filetype,
                filename=filename
                )
        filepath = generic_filename + "." + filetype

        image_file = "{dirpath}/images/{filename}.png".format(
                dirpath=dirpath,
                filename=filename
                )
        qr_image_file = self.make_qr_code(fragment);
        qr_image_file.save(image_file)

        d = {
            'label': self.label,
            'timestamp': datetime.datetime.now().strftime("%d-%b-%Y %H:%M:%S"),
            'report': self.report,
            'contact_name': self.config['contact']['name'],
            'contact_email': self.config['contact']['email'],
            'fragment': fragment,
            'img_src': image_file 
        }
        template_type = "md" if filetype == "md" else "html"
        filein = open("text/fragment." + template_type)
        src = Template(filein.read())
        filein.close()
        content = src.substitute(d)
        if filetype == "pdf":
            pdf = pydf.generate_pdf(content, image_quality=100, image_dpi=1000)
            with open(filepath, 'wb') as f:
                f.write(pdf)
        else:
            self.write_file(filepath, content)

    def make_qr_code(self, fragment):
        """Makes a QR Code from a string - the secret fragment."""
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
        """Create a document with user instructions.i
            
            Parameters: Root directory of the generated fragment files.
        """
        d = {
            'label': self.label,
            'timestamp': datetime.datetime.now().strftime("%d-%b-%Y %H:%M:%S")
        }
        filein = open("text/readme.txt")
        src = Template(filein.read())
        readme_content = src.substitute(d)
        readme = dir / "README.md"
        file = open(readme, 'w')
        file.write(textwrap.dedent(readme_content))
        file.close()

    def clean_up(self):
        """Securely delete sensitive material.

        Uses GNU shred utility (https://www.gnu.org/software/coreutils/manual/html_node/shred-invocation.html)
        This should be available on TAILS.
        """
        print("Your secrets have been split and saved as individual files. Holding these files in one place is a security vulnerability.")
        print("Files:")
        pathlist = Path(self.dir).glob('**/*')
        for path in pathlist:
            print(path)
        if click.confirm("Do you want to securely shred the files?", default=True):
            # TODO: References incorrect file paths - fix this. Should shred all png, pdf, html, md
            pathlist = Path(self.dir).glob('**/*.txt')
            for index, path in enumerate(pathlist):
                print("_shredding {}...".format(str(path)))
                cmd = ['shred', '-vfzu', str(path)]
                stdoutdata = subprocess.check_output(cmd).decode('utf-8')
                print("stdoutdata: " + stdoutdata)
