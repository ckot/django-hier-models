import os
from setuptools import find_packages, setup

__VERSION__ = '0.1.3'


with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-hier-models',
    version=__VERSION__,
    packages=find_packages(),
    include_package_data=True,
    license='Proprietary',  # example license
    description='foo',
    long_description=README,
    url='https://github.com/ckot/django-hier-models/',
    author='Scott Silliman',
    author_email='scott.t.silliman@gmail.com',
    classifiers=[
        'Private :: Do Not Upload'
    ],
)