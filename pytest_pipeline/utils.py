# -*- coding: utf-8 -*-
"""
    pytest_pipeline.utils
    ~~~~~~~~~~~~~~~~~~~~~

    General utilities.

    :copyright: (c) 2014 Wibowo Arindrarto <bow@bow.web.id>
    :license: BSD

"""

import gzip
import hashlib
import os


def file_md5sum(fname, unzip=False, blocksize=65536, encoding="utf-8"):
    if unzip:
        opener = gzip.open
    else:
        opener = open

    hasher = hashlib.md5()
    with opener(fname, "rb") as src:
        buf = src.read(blocksize)
        while len(buf) > 0:
            hasher.update(buf)
            buf = src.read(blocksize)
    return hasher.hexdigest()


def isexecfile(fname):
    return os.path.isfile(fname) and os.access(fname, os.X_OK)


def which(program):
    # can not do anything meaningful without PATH
    if "PATH" not in os.environ:
        return
    for possible in os.environ["PATH"].split(":"):
        qualname = os.path.join(possible, program)
        if isexecfile(qualname):
            return qualname
    return
