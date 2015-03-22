# -*- coding: utf-8 -*-
"""
    pytest_pipeline.plugin
    ~~~~~~~~~~~~~~~~~~~~~~

    pytest plugin entry point.

    :copyright: (c) 2014 Wibowo Arindrarto <bow@bow.web.id>
    :license: BSD

"""

## credits to Holger Krekel himself for these xfail marking functions
## http://stackoverflow.com/a/12579625/243058
def pytest_runtest_makereport(item, call):
    if "xfail_pipeline" in item.keywords:
        if call.excinfo is not None:
            parent = item.parent
            parent._previousfailed = item


def pytest_addoption(parser):
    group = parser.getgroup("general")
    group.addoption("--base-pipeline-dir", dest="base_pipeline_dir",
                    default=None, metavar="dir",
                    help="Base directory to put all pipeline test directories")
    group.addoption("--xfail-pipeline", dest="xfail_pipeline", action="store_true",
                    default=False,
                    help="Whether to fail a class immediately if any of its tests fail")
