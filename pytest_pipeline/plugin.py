# -*- coding: utf-8 -*-
"""
    pytest_pipeline.plugin
    ~~~~~~~~~~~~~~~~~~~~~~

    pytest plugin entry point.

    :copyright: (c) 2014 Wibowo Arindrarto <bow@bow.web.id>
    :license: BSD

"""

import os
import shutil
import tempfile
from itertools import groupby

import pytest

from .mark import UNMARKED, AFTER_RUN


@pytest.fixture(scope="class")
def _autogendir(request):
    run_dir = request.cls.test_dirname
    init_dir = os.getcwd()
    # create base pipeline dir if it does not exist
    root_test_dir = request.config.option.base_pipeline_dir
    if root_test_dir is None:
        tmpdir = os.path.join(tempfile.tempdir, "pipeline_tests")
        if not os.path.exists(tmpdir):
            os.makedirs(tmpdir)
        root_test_dir = tempfile.mkdtemp(dir=tmpdir)
    if not os.path.exists(root_test_dir):
        os.makedirs(root_test_dir)
    test_dir = os.path.join(root_test_dir, run_dir)
    # TODO: warn if we are removing existing directory?
    if os.path.exists(test_dir):
        shutil.rmtree
    os.makedirs(test_dir)
    def done(): os.chdir(init_dir)
    request.addfinalizer(done)
    os.chdir(test_dir)


def pytest_collection_modifyitems(session, config, items):

    # maintain order of class found by pytest
    # TODO: how to maintain order of standalone test functions (i.e. not in a class)
    # TODO: how to maintain order of item in one type (e.g. all before_run)?

    def _test_group_key(item):
        try:
            return item.cls.__name__
        except AttributeError:
            return item.function.__name__

    class_order = {grouped[0]: i for i, grouped in
                   enumerate(groupby(items, key=_test_group_key))}

    def _test_sort_key(item):
        phase_data = getattr(item.function, "_pipeline", None)
        # use -1 score for unmarked functions
        marked_order = UNMARKED
        within_mark_order = 0
        if phase_data is not None:
            marked_order = phase_data["phase"]
            within_mark_order = phase_data["order"]
        try:
            return class_order[item.cls.__name__], marked_order, \
                    within_mark_order
        except AttributeError:
            return class_order[item.function.__name__], marked_order, \
                    within_mark_order

    items[:] = sorted(items, key=_test_sort_key)


## credits to Holger Krekel himself for these xfail marking functions
## http://stackoverflow.com/a/12579625/243058
def pytest_runtest_makereport(item, call):
    if "xfail_pipeline" in item.keywords:
        if call.excinfo is not None:
            parent = item.parent
            parent._previousfailed = item


def pytest_runtest_setup(item):
    # skip run and all after_run when config option is set
    if item.config.option.skip_run \
        and hasattr(item, 'cls') \
        and item.function.func_dict.get('_pipeline', {}).get('phase') == AFTER_RUN:
            pytest.skip(msg="'{0}' class does not have any 'run' "
                        "objects".format(item.cls))
    # incremental failure marking when the first pipeline_run test fails
    previousfailed = getattr(item.parent, "_previousfailed", None)
    if previousfailed is not None and item.config.option.xfail_pipeline:
        pytest.xfail("Previous test failed: '{0}'".format(previousfailed.name))


def pytest_addoption(parser):
    group = parser.getgroup("general")
    group.addoption("--base-pipeline-dir", dest="base_pipeline_dir",
                    default=None, metavar="dir",
                    help="Base directory to put all pipeline test directories")
    group.addoption("--xfail-pipeline", dest="xfail_pipeline", action="store_true",
                    default=False,
                    help="Whether to fail a class immediately if any of its tests fail")
    group.addoption("--skip-run", dest="skip_run", action="store_true",
                    default=False,
                    help="Whether to skip the pipeline run and all tests after it")
