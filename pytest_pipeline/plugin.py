# -*- coding: utf-8 -*-
"""
    pytest_pipeline.plugin
    ~~~~~~~~~~~~~~~~~~~~~~

    pytest plugin entry point.

"""
# (c) 2014-2018 Wibowo Arindrarto <bow@bow.web.id>


def pytest_addoption(parser):
    group = parser.getgroup("general")
    group.addoption("--base-pipeline-dir", dest="base_pipeline_dir",
                    default=None, metavar="dir",
                    help="Base directory to put all pipeline test directories")
