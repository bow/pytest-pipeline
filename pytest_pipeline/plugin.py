# -*- coding: utf-8 -*-
"""
    pytest_pipeline.plugin
    ~~~~~~~~~~~~~~~~~~~~~~

    pytest plugin entry point.

    :copyright: (c) 2014 Wibowo Arindrarto <bow@bow.web.id>
    :license: BSD

"""

def pytest_addoption(parser):
    group = parser.getgroup("general")
    group.addoption("--base-pipeline-dir", dest="base_pipeline_dir",
                    default=None, metavar="dir",
                    help="Base directory to put all pipeline test directories")
