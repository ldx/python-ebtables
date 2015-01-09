# from distutils.core import setup
from setuptools import setup

"""python-ebtables setup script"""

import ebtables

setup(
    name='ebtables',
    version=ebtables.__version__,
    author='Vilmos Nebehaj',
    author_email='v.nebehaj@gmail.com',
    url='https://github.com/ldx/python-ebtables',
    description='Linux Ebtables bindings',
    py_modules=['ebtables'],
    setup_requires=['cffi'],
    install_requires=['cffi'],
    ext_modules=[ebtables.ffi.verifier.get_extension()],
    zip_safe=False,
)
