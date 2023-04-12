# encoding: UTF-8
from setuptools import find_packages, setup
import os

setup(
    name='collerecei',
    version='2023.4',
    license='PolyForm Shield License 1.0.0',
    description='領収書自動取得ツール これれし',
    author='sanofujiwarak',
    author_email='7044283+sanofujiwarak@users.noreply.github.com',
    url='',
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    packages=find_packages(),
    python_requires='==3.9.*',
    install_requires=open(f'requirements{os.sep}base.txt').read().splitlines(),
)
