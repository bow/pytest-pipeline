#TODO: unit tests ~ these are closer to integration/functional tests
import glob
import os
import sys

import pytest


pytest_plugins = "pytester"


MOCK_PIPELINE = """
#!/usr/bin/env python

if __name__ == "__main__":

    import os
    import sys

    OUT_DIR = "output_dir"

    if len(sys.argv) > 1:
        sys.exit(1)

    sys.stdout.write("stdout stream")
    sys.stderr.write("stderr stream")

    with open("log.txt", "w") as log:
        log.write("not really\\n")

    if not os.path.exists(OUT_DIR):
        os.makedirs(OUT_DIR)

    with open(os.path.join(OUT_DIR, "results.txt"), "w") as result:
        result.write("42\\n")
"""

@pytest.fixture(scope="function")
def mockpipe(request, testdir):
    """Mock pipeline script"""
    mp = testdir.makefile("", pipeline=MOCK_PIPELINE)
    return mp


TEST_OK = """
import os, shutil, unittest
import pytest
from pytest_pipeline import PipelineRun, mark

class MyRun(PipelineRun):

    @mark.before_run
    def prep_executable(self):
        shutil.copy2("../pipeline", "pipeline")
        assert os.path.exists("pipeline")

run = MyRun.make_fixture("class", "{python} pipeline")

@pytest.mark.usefixtures("run")
class TestMyPipeline(unittest.TestCase):

    def test_exit_code(self):
        assert self.run_fixture.exit_code == 0
""".format(python=sys.executable)


def test_pipeline_basic(mockpipe, testdir):
    """Test for basic run"""
    test = testdir.makepyfile(TEST_OK)
    result = testdir.runpytest("-v", "--base-pipeline-dir=" + test.dirname, test)
    result.stdout.fnmatch_lines([
        "* collected 1 items"
    ])
    expected = [False]
    linenos = [0]
    for lineno, line in enumerate(result.outlines, start=1):
        if line.endswith("TestMyPipeline::test_exit_code PASSED"):
            expected[0] = True
            linenos[0] = lineno
    assert all(expected), "Not all tests in mock pipeline test found"


TEST_OK_CLASS_FIXTURE = """
import os, shutil, unittest
import pytest
from pytest_pipeline import PipelineRun, mark

class MyRun(PipelineRun):

    @mark.before_run
    def prep_executable(self):
        shutil.copy2("../pipeline", "pipeline")
        assert os.path.exists("pipeline")

run = MyRun.class_fixture("{python} pipeline")

@pytest.mark.usefixtures("run")
class TestMyPipelineAgain(unittest.TestCase):

    def test_exit_code(self):
        assert self.run_fixture.exit_code == 0
""".format(python=sys.executable)


def test_pipeline_class_fixture(mockpipe, testdir):
    """Test for basic run"""
    test = testdir.makepyfile(TEST_OK_CLASS_FIXTURE)
    result = testdir.runpytest("-v", "--base-pipeline-dir=" + test.dirname, test)
    result.stdout.fnmatch_lines([
        "* collected 1 items"
    ])
    expected = [False]
    linenos = [0]
    for lineno, line in enumerate(result.outlines, start=1):
        if line.endswith("TestMyPipelineAgain::test_exit_code PASSED"):
            expected[0] = True
            linenos[0] = lineno
    assert all(expected), "Not all tests in mock pipeline test found"


TEST_REDIRECTION = """
import os, shutil, unittest
import pytest
from pytest_pipeline import PipelineRun, mark

class MyRun(PipelineRun):

    @mark.before_run
    def prep_executable(self):
        shutil.copy2("../pipeline", "pipeline")
        assert os.path.exists("pipeline")

run = MyRun.make_fixture("class", cmd="{python} pipeline",
                               stdout="stream.out",
                               stderr="stream.err")

@pytest.mark.usefixtures("run")
class TestMyPipeline(unittest.TestCase):

    def test_exit_code(self):
        assert self.run_fixture.exit_code == 0
""".format(python=sys.executable)


def test_pipeline_redirection(mockpipe, testdir):
    test = testdir.makepyfile(TEST_REDIRECTION)
    result = testdir.runpytest("-v", "--base-pipeline-dir=" + test.dirname, test)
    result.stdout.fnmatch_lines([
        "*TestMyPipeline::test_exit_code PASSED",
    ])
    testdir_matches = glob.glob(os.path.join(test.dirname, "MyRun*"))
    assert len(testdir_matches) == 1
    testdir_pipeline = testdir_matches[0]
    stdout = os.path.join(testdir_pipeline, "stream.out")
    assert os.path.exists(stdout)
    assert open(stdout).read() == "stdout stream"
    stderr = os.path.join(testdir_pipeline, "stream.err")
    assert os.path.exists(stderr)
    assert open(stderr).read() == "stderr stream"


TEST_AS_NONCLASS_FIXTURE = """
import os, shutil, unittest
import pytest
from pytest_pipeline import PipelineRun, mark

class MyRun(PipelineRun):

    @mark.before_run
    def prep_executable(self):
        shutil.copy2("../pipeline", "pipeline")
        assert os.path.exists("pipeline")

run = MyRun.make_fixture("module", "{python} pipeline")

def test_exit_code(run):
    assert run.exit_code == 0
""".format(python=sys.executable)


def test_pipeline_as_nonclass_fixture(mockpipe, testdir):
    """Test for PipelineTest classes without run attribute"""
    test = testdir.makepyfile(TEST_AS_NONCLASS_FIXTURE)
    result = testdir.runpytest("-v", "--base-pipeline-dir=" + test.dirname, test)
    result.stdout.fnmatch_lines([
        "* collected 1 items"
    ])
    expected = [False]
    linenos = [0]
    for lineno, line in enumerate(result.outlines, start=1):
        if line.endswith("test_pipeline_as_nonclass_fixture.py::test_exit_code PASSED"):
            expected[0] = True
            linenos[0] = lineno
    assert all(expected), "Not all tests in mock pipeline test found"


TEST_OK_GRANULAR = """
import os, shutil, unittest
import pytest
from pytest_pipeline import PipelineRun, mark

class MyRun(PipelineRun):

    @mark.before_run(order=2)
    def prep_executable(self):
        shutil.copy2("../pipeline", "pipeline")
        assert os.path.exists("pipeline")

    @mark.before_run(order=1)
    def check_init_condition(self):
        assert not os.path.exists("pipeline")

run = MyRun.make_fixture("class", cmd="{python} pipeline")

@pytest.mark.usefixtures("run")
class TestMyPipeline(unittest.TestCase):

    def test_exit_code(self):
        assert self.run_fixture.exit_code == 0

    def test_output_file(self):
        assert os.path.exists(os.path.join("output_dir", "results.txt"))
""".format(python=sys.executable)


def test_pipeline_granular(mockpipe, testdir):
    """Test for execution with 'order' specified in before_run and after_run"""
    test = testdir.makepyfile(TEST_OK_GRANULAR)
    result = testdir.runpytest("-v", "--base-pipeline-dir=" + test.dirname, test)
    result.stdout.fnmatch_lines([
        "* collected 2 items"
    ])
    expected = [False, False]
    linenos = [0, 0]
    for lineno, line in enumerate(result.outlines, start=1):
        if line.endswith("TestMyPipeline::test_exit_code PASSED"):
            expected[0] = True
            linenos[0] = lineno
        elif line.endswith("TestMyPipeline::test_output_file PASSED"):
            expected[1] = True
            linenos[1] = lineno
    assert all(expected), "Not all tests in mock pipeline test executed"
    assert linenos == sorted(linenos), "Mock pipeline test sorted in wrong order"


MOCK_PIPELINE_TIMEOUT = """
#!/usr/bin/env python

if __name__ == "__main__":

    import time
    time.sleep(10)
"""


TEST_TIMEOUT = """
import os, shutil, unittest
import pytest
from pytest_pipeline import PipelineRun, mark

class MyRun(PipelineRun):

    @mark.before_run
    def test_and_prep_executable(self):
        shutil.copy2("../pipeline", "pipeline")
        assert os.path.exists("pipeline")

run = PipelineRun.make_fixture("class", cmd="{python} pipeline",
                                     timeout=0.01)

@pytest.mark.usefixtures("run")
class TestMyPipeline(unittest.TestCase):

    def test_exit_code(self):
        assert self.run_fixture.exit_code != 0
""".format(python=sys.executable)


@pytest.fixture(scope="function")
def mockpipe_timeout(request, testdir):
    """Mock pipeline script with timeout"""
    mp = testdir.makefile("", pipeline=MOCK_PIPELINE_TIMEOUT)
    return mp


def test_pipeline_timeout(mockpipe_timeout, testdir):
    """Test for execution with timeout"""
    test = testdir.makepyfile(TEST_TIMEOUT)
    result = testdir.runpytest("-v", "--base-pipeline-dir=" + test.dirname, test)
    result.stdout.fnmatch_lines([
        "* collected 1 items",
        "*Failed: Process is taking longer than 0.01 seconds",
    ])
