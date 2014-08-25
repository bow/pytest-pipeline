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
import os, shutil
from pytest_pipeline import PipelineRun, PipelineTest, mark

class TestMyPipeline(PipelineTest):

    run = PipelineRun(cmd="{python} pipeline")

    @mark.before_run
    def test_and_prep_executable(self):
        shutil.copy2("../pipeline", "pipeline")
        assert os.path.exists("pipeline")

    @mark.after_run
    def test_exit_code(self):
        assert self.run.exit_code == 0
""".format(python=sys.executable)


def test_pipeline_basic(mockpipe, testdir):
    """Test for basic execution order: before_run then after_run"""
    test = testdir.makepyfile(TEST_OK)
    result = testdir.runpytest("-v", "--base-pipeline-dir=" + test.dirname, test)
    result.stdout.fnmatch_lines([
        "* collected 2 items"
    ])
    expected = [False, False]
    linenos = [0, 0]
    for lineno, line in enumerate(result.outlines, start=1):
        if line.endswith("TestMyPipeline::test_and_prep_executable PASSED"):
            expected[0] = True
            linenos[0] = lineno
        elif line.endswith("TestMyPipeline::test_exit_code PASSED"):
            expected[1] = True
            linenos[1] = lineno
    assert all(expected), "Not all tests in mock pipeline test found"
    assert linenos[0] < linenos[1], "Mock pipeline test sorted in wrong order"


TEST_REDIRECTION = """
import os, shutil
from pytest_pipeline import PipelineRun, PipelineTest, mark

class TestMyPipeline(PipelineTest):

    run = PipelineRun(
        cmd="{python} pipeline",
        stdout="stream.out",
        stderr="stream.err",
    )

    @mark.before_run
    def test_and_prep_executable(self):
        shutil.copy2("../pipeline", "pipeline")
        assert os.path.exists("pipeline")

    @mark.after_run
    def test_exit_code(self):
        assert self.run.exit_code == 0
""".format(python=sys.executable)


def test_pipeline_redirection(mockpipe, testdir):
    test = testdir.makepyfile(TEST_REDIRECTION)
    result = testdir.runpytest("-v", "--base-pipeline-dir=" + test.dirname, test)
    result.stdout.fnmatch_lines([
        "*TestMyPipeline::test_exit_code PASSED",
    ])
    testdir_matches = glob.glob(os.path.join(test.dirname, "TestMyPipeline*"))
    assert len(testdir_matches) == 1
    testdir_pipeline = testdir_matches[0]
    stdout = os.path.join(testdir_pipeline, "stream.out")
    assert os.path.exists(stdout)
    assert open(stdout).read() == "stdout stream"
    stderr = os.path.join(testdir_pipeline, "stream.err")
    assert os.path.exists(stderr)
    assert open(stderr).read() == "stderr stream"


TEST_NORUN = """
import os, shutil
from pytest_pipeline import PipelineRun, PipelineTest, mark

class TestMyPipeline(PipelineTest):

    @mark.before_run
    def test_and_prep_executable(self):
        shutil.copy2("../pipeline", "pipeline")
        assert os.path.exists("pipeline")

    @mark.after_run
    def test_exit_code(self):
        assert self.run.exit_code == 0

    def test_standalone(self):
        assert 1 == 1
""".format(python=sys.executable)


def test_pipeline_no_run(testdir):
    """Test for PipelineTest classes without run attribute"""
    test = testdir.makepyfile(TEST_NORUN)
    result = testdir.runpytest("-v", "--base-pipeline-dir=" + test.dirname, test)
    result.stdout.fnmatch_lines([
        "* collected 3 items"
    ])
    expected = [False, False]
    linenos = [0, 0]
    for lineno, line in enumerate(result.outlines, start=1):
        if line.endswith("TestMyPipeline::test_and_prep_executable SKIPPED"):
            expected[0] = True
            linenos[0] = lineno
        elif line.endswith("TestMyPipeline::test_exit_code SKIPPED"):
            expected[1] = True
            linenos[1] = lineno
    assert all(expected), "Not all tests in mock pipeline test executed"
    assert linenos[0] < linenos[1], "Mock pipeline test sorted in wrong order"
    result.stdout.fnmatch_lines([
        "*TestMyPipeline::test_standalone PASSED",
    ])


TEST_OK_WITH_NONCLASS = TEST_OK + """

def test_function_standalone():
    assert 1 == 1
"""

def test_pipeline_with_function(mockpipe, testdir):
    """Test for basic execution order with non-class-based test."""
    test = testdir.makepyfile(TEST_OK_WITH_NONCLASS)
    result = testdir.runpytest("-v", "--base-pipeline-dir=" + test.dirname, test)
    result.stdout.fnmatch_lines([
        "* collected 3 items"
    ])
    expected = [False, False]
    linenos = [0, 0]
    for lineno, line in enumerate(result.outlines, start=1):
        if line.endswith("TestMyPipeline::test_and_prep_executable PASSED"):
            expected[0] = True
            linenos[0] = lineno
        elif line.endswith("TestMyPipeline::test_exit_code PASSED"):
            expected[1] = True
            linenos[1] = lineno
    assert all(expected), "Not all tests in mock pipeline test executed"
    assert linenos[0] < linenos[1], "Mock pipeline test sorted in wrong order"


TEST_OK_GRANULAR = """
import os, shutil
from pytest_pipeline import PipelineRun, PipelineTest, mark

class TestMyPipeline(PipelineTest):

    run = PipelineRun(cmd="{python} pipeline")

    @mark.before_run(order=2)
    def test_and_prep_executable(self):
        shutil.copy2("../pipeline", "pipeline")
        assert os.path.exists("pipeline")

    @mark.before_run(order=1)
    def test_init_condition(self):
        assert not os.path.exists("pipeline")

    @mark.after_run(order=1)
    def test_exit_code(self):
        assert self.run.exit_code == 0

    @mark.after_run(order=2)
    def test_output_file(self):
        assert os.path.exists(os.path.join("output_dir", "results.txt"))
""".format(python=sys.executable)


def test_pipeline_granular(mockpipe, testdir):
    """Test for execution with 'order' specified in before_run and after_run"""
    test = testdir.makepyfile(TEST_OK_GRANULAR)
    result = testdir.runpytest("-v", "--base-pipeline-dir=" + test.dirname, test)
    result.stdout.fnmatch_lines([
        "* collected 4 items"
    ])
    expected = [False, False, False, False]
    linenos = [0, 0, 0, 0]
    for lineno, line in enumerate(result.outlines, start=1):
        if line.endswith("TestMyPipeline::test_init_condition PASSED"):
            expected[0] = True
            linenos[0] = lineno
        elif line.endswith("TestMyPipeline::test_and_prep_executable PASSED"):
            expected[1] = True
            linenos[1] = lineno
        elif line.endswith("TestMyPipeline::test_exit_code PASSED"):
            expected[2] = True
            linenos[2] = lineno
        elif line.endswith("TestMyPipeline::test_output_file PASSED"):
            expected[3] = True
            linenos[3] = lineno
    assert all(expected), "Not all tests in mock pipeline test executed"
    assert linenos == sorted(linenos), "Mock pipeline test sorted in wrong order"


MOCK_PIPELINE_TIMEOUT = """
#!/usr/bin/env python

if __name__ == "__main__":

    import time
    time.sleep(10)
"""


TEST_TIMEOUT = """
import os, shutil
from pytest_pipeline import PipelineRun, PipelineTest, mark

class TestMyPipeline(PipelineTest):

    run = PipelineRun(cmd="{python} pipeline", timeout=0.1)

    @mark.before_run
    def test_and_prep_executable(self):
        shutil.copy2("../pipeline", "pipeline")
        assert os.path.exists("pipeline")

    @mark.after_run
    def test_exit_code(self):
        assert self.run.exit_code != 0
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
        "* collected 2 items",
        "*Failed: Process is taking longer than 0.1 seconds",
    ])
