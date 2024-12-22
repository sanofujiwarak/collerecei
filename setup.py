# encoding: UTF-8
from setuptools import find_packages, setup
import os

from collerecei.version import __version__

setup(
    name='collerecei',
    version=__version__,
    license='PolyForm Shield License 1.0.0',
    description='領収書自動取得ツール これれし',
    author='sanofujiwarak',
    author_email='7044283+sanofujiwarak@users.noreply.github.com',
    url='https://collerecei.tssol.net',
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    packages=find_packages(),
    python_requires='>=3.9',
    install_requires=open(f'requirements{os.sep}base.txt').read().splitlines(),
)
