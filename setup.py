


# https://github.com/pypa/sampleproject/blob/master/setup.py

from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='Visinum',
    version='0.2.0',
    description='Project to improve engineering computational productivity.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/qwilka/Visinum',
    author='Stephen McEntee',
    author_email='stephenmce@gmail.com',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Operating System :: POSIX :: Linux',
        'Topic :: Scientific/Engineering',
        'Intended Audience :: Science/Research',
        'Natural Language :: English',
    ],
    keywords='science engineering computational productivity',
    packages=find_packages(exclude=['docs', 'examples']),
    python_requires='>=3.6',
    install_requires=[
        "pymongo",
        "vntree",
    ],
)
