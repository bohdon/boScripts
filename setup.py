import sys, os
from distutils.core import setup

srcdir = os.path.abspath(os.path.join(os.path.dirname(__file__),'src'))

# get all files and folders within ./src
fileList = []
for root, dirs, files in os.walk(srcdir):
    for file_ in files:
        fileList.append( os.path.relpath(os.path.join(root, file_), srcdir))
fileDirDict = {}
for file_ in fileList:
    dir_ = os.path.dirname(file_)
    if not fileDirDict.has_key(dir_):
        fileDirDict[dir_] = []
    fileDirDict[dir_].append(os.path.join('src', file_))
data_files = [(key, value) for key, value in fileDirDict.items()]


setup(
    name='boScripts',
    version='0.0.1',
    data_files=data_files,
)