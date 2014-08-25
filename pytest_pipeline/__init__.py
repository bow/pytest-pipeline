# -*- coding: utf-8 -*-
"""
    pytest_pipeline
    ~~~~~~~~~~~~~~~

    Pytest plugin for functional testing of data analysis pipelines.

    :copyright: (c) 2014 Wibowo Arindrarto <bow@bow.web.id>
    :license: BSD

"""

RELEASE = True

__version_info__ = ("0", "1", "0")
__version__ = ".".join(__version_info__)
__version__ += "-dev" if not RELEASE else ""

__author__ = "Wibowo Arindrarto"
__contact__ = "bow@bow.web.id"
__homepage__ = "https://github.com/bow/pytest_pipeline"


from .core import PipelineRun, PipelineTest
