import sys
import os
from distutils.core import setup
root = os.path.abspath(os.path.dirname(__file__))
distRoot = os.path.join(root, 'src')

def get_data_files(dir_, root, distRoot=None):
    """
    Return a list of directory:[files] for use in distutils setup function
    
    `dir_` -- the absolute path to the directory to be searched
    `root` -- the path to the directory searched by setuptools
    `distRoot` -- the path to the root dir that will be distributed; data files
                  will have paths that match their relative path to distRoot.
                  default is root
    """
    if distRoot is None:
        distRoot = root
    fileList = []
    for root_, dirs, files in os.walk(dir_):
        for file_ in files:
            fileList.append( os.path.join(root_, file_) )
    # convert file list to data files format
    fileDict = {}
    for file_ in fileList:
        dir_ = os.path.relpath( os.path.dirname(file_), distRoot )
        if not fileDict.has_key(dir_):
            fileDict[dir_] = []
        fileDict[dir_].append(os.path.relpath(file_, root))
    return [(k, v) for k, v in fileDict.items()]


data_files = get_data_files(distRoot, root, distRoot)

setup(
    name='boScripts',
    version='0.1.2',
    data_files=data_files,
)