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


def file_md5sum(fname, unzip=False, mode="r", blocksize=65536):
    if unzip:
        opener = gzip.open
    else:
        opener = open

    hasher = hashlib.md5()
    with opener(fname, mode) as src:
        buf = src.read(blocksize)
        while len(buf) > 0:
            hasher.update(buf)
            buf = src.read(blocksize)
    return hasher.hexdigest()
