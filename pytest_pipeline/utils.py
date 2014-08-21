# -*- coding: utf-8 -*-
"""
    pytest_pipeline.utils
    ~~~~~~~~~~~~~~~~~~~~~

    General utilities.

    :copyright: (c) 2014 Wibowo Arindrarto <bow@bow.web.id>
    :license: BSD

"""

import hashlib


def md5sum_from_file(fname, opener=open, mode="r", blocksize=65536):
    hasher = hashlib.md5()
    with opener(fname, mode) as src:
        buf = src.read(blocksize)
        while len(buf) > 0:
            hasher.update(buf)
            buf = src.read(blocksize)
    return hasher.hexdigest()
