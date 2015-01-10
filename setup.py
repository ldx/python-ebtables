import os
import subprocess
from setuptools import setup

"""python-ebtables setup script"""

import ebtables

long_description = """Ebtables is used for Ethernet bridge frame table
administration on Linux. Python-ebtables is a simple Python binding for
Ebtables."""

try:
    create_rst = True
    if os.path.exists('README.rst'):
        s1 = os.stat('README.md')
        s2 = os.stat('README.rst')
        if s1.st_mtime <= s2.st_mtime:
            create_rst = False
    if create_rst:
        rc = subprocess.call(['pandoc',
                              '-o', 'README.rst',
                              '-f', 'markdown',
                              '-t', 'rst',
                              'README.md'],
                             shell=False,
                             stdout=subprocess.PIPE)
        if rc == 0:
            with open('README.rst') as f:
                long_description = f.read()
except:
    pass


setup(
    name='ebtables',
    version=ebtables.__version__,
    author='Vilmos Nebehaj',
    author_email='v.nebehaj@gmail.com',
    url='https://github.com/ldx/python-ebtables',
    description='Linux Ebtables bindings',
    long_description=long_description,
    py_modules=['ebtables'],
    setup_requires=['cffi'],
    install_requires=['cffi'],
    ext_modules=[ebtables.ffi.verifier.get_extension()],
    zip_safe=False,
)
