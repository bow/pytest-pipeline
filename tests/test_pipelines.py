# -*- coding: utf-8 -*-
"""
    plugin tests
    ~~~~~~~~~~~~

"""
# (c) 2014-2020 Wibowo Arindrarto <bow@bow.web.id>

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


TEST_OK = f"""
import os, shutil, unittest

import pytest

from pytest_pipeline import PipelineRun, mark


class MyRun(PipelineRun):

    @mark.before_run
    def prep_executable(self):
        shutil.copy2("../pipeline", "pipeline")
        assert os.path.exists("pipeline")


run = MyRun.make_fixture("class", "{sys.executable} pipeline")


@pytest.mark.usefixtures("run")
class TestMyPipeline(unittest.TestCase):

    def test_exit_code(self):
        assert self.run_fixture.exit_code == 0
"""


def test_pipeline_basic(mockpipe, testdir):
    """Test for basic run"""
    test = testdir.makepyfile(TEST_OK)
    result = testdir.inline_run(
        "-v",
        f"--base-pipeline-dir={test.dirname}",
        test
    )
    passed, skipped, failed = result.listoutcomes()

    assert len(passed) == 1
    assert len(skipped) == 0
    assert len(failed) == 0


TEST_OK_CLASS_FIXTURE = f"""
import os, shutil, unittest

import pytest

from pytest_pipeline import PipelineRun, mark


class MyRun(PipelineRun):

    @mark.before_run
    def prep_executable(self):
        shutil.copy2("../pipeline", "pipeline")
        assert os.path.exists("pipeline")


run = MyRun.class_fixture("{sys.executable} pipeline")


@pytest.mark.usefixtures("run")
class TestMyPipelineAgain(unittest.TestCase):

    def test_exit_code(self):
        assert self.run_fixture.exit_code == 0
"""


def test_pipeline_class_fixture(mockpipe, testdir):
    """Test for basic run"""
    test = testdir.makepyfile(TEST_OK_CLASS_FIXTURE)
    result = testdir.inline_run(
        "-v",
        f"--base-pipeline-dir={test.dirname}",
        test
    )
    passed, skipped, failed = result.listoutcomes()

    assert len(passed) == 1
    assert len(skipped) == 0
    assert len(failed) == 0


TEST_REDIRECTION = f"""
import os, shutil, unittest

import pytest

from pytest_pipeline import PipelineRun, mark


class MyRun(PipelineRun):

    @mark.before_run
    def prep_executable(self):
        shutil.copy2("../pipeline", "pipeline")
        assert os.path.exists("pipeline")


run = MyRun.make_fixture(
    "class",
    cmd="{sys.executable} pipeline",
    stdout="stream.out",
    stderr="stream.err",
)


@pytest.mark.usefixtures("run")
class TestMyPipeline(unittest.TestCase):

    def test_exit_code(self):
        assert self.run_fixture.exit_code == 0
"""


def test_pipeline_redirection(mockpipe, testdir):
    test = testdir.makepyfile(TEST_REDIRECTION)
    result = testdir.inline_run(
        "-v",
        f"--base-pipeline-dir={test.dirname}",
        test
    )
    passed, skipped, failed = result.listoutcomes()

    assert len(passed) == 1
    assert len(skipped) == 0
    assert len(failed) == 0

    testdir_matches = glob.glob(os.path.join(test.dirname, "MyRun*"))

    assert len(testdir_matches) == 1

    testdir_pipeline = testdir_matches[0]
    stdout = os.path.join(testdir_pipeline, "stream.out")

    assert os.path.exists(stdout)
    assert open(stdout).read() == "stdout stream"

    stderr = os.path.join(testdir_pipeline, "stream.err")

    assert os.path.exists(stderr)
    assert open(stderr).read() == "stderr stream"


TEST_REDIRECTION_MEM = f"""
import os, shutil, unittest

import pytest

from pytest_pipeline import PipelineRun, mark


class MyRun(PipelineRun):

    @mark.before_run
    def prep_executable(self):
        shutil.copy2("../pipeline", "pipeline")
        assert os.path.exists("pipeline")


run = MyRun.make_fixture(
    "class",
    cmd="{sys.executable} pipeline",
    stdout=True,
    stderr=True,
)


@pytest.mark.usefixtures("run")
class TestMyPipeline(unittest.TestCase):

    def test_exit_code(self):
        assert self.run_fixture.exit_code == 0

    def test_stdout(self):
        assert self.run_fixture.stdout == b"stdout stream"

    def test_stderr(self):
        assert self.run_fixture.stderr == b"stderr stream"
"""


def test_pipeline_redirection_mem(mockpipe, testdir):
    test = testdir.makepyfile(TEST_REDIRECTION_MEM)
    result = testdir.inline_run(
        "-v",
        f"--base-pipeline-dir={test.dirname}",
        test
    )
    passed, skipped, failed = result.listoutcomes()

    assert len(passed) == 3
    assert len(skipped) == 0
    assert len(failed) == 0

    testdir_matches = glob.glob(os.path.join(test.dirname, "MyRun*"))

    assert len(testdir_matches) == 1


TEST_AS_NONCLASS_FIXTURE = f"""
import os, shutil, unittest

import pytest

from pytest_pipeline import PipelineRun, mark


class MyRun(PipelineRun):

    @mark.before_run
    def prep_executable(self):
        shutil.copy2("../pipeline", "pipeline")
        assert os.path.exists("pipeline")


run = MyRun.make_fixture("module", "{sys.executable} pipeline")


def test_exit_code(run):
    assert run.exit_code == 0
"""


def test_pipeline_as_nonclass_fixture(mockpipe, testdir):
    """Test for PipelineTest classes without run attribute"""
    test = testdir.makepyfile(TEST_AS_NONCLASS_FIXTURE)
    result = testdir.inline_run(
        "-v",
        f"--base-pipeline-dir={test.dirname}",
        test
    )
    passed, skipped, failed = result.listoutcomes()

    assert len(passed) == 1
    assert len(skipped) == 0
    assert len(failed) == 0


TEST_OK_GRANULAR = f"""
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


run = MyRun.make_fixture("class", cmd="{sys.executable} pipeline")


@pytest.mark.usefixtures("run")
class TestMyPipeline(unittest.TestCase):

    def test_exit_code(self):
        assert self.run_fixture.exit_code == 0

    def test_output_file(self):
        assert os.path.exists(os.path.join("output_dir", "results.txt"))
"""


def test_pipeline_granular(mockpipe, testdir):
    """Test for execution with 'order' specified in before_run and after_run"""
    test = testdir.makepyfile(TEST_OK_GRANULAR)
    result = testdir.inline_run(
        "-v",
        f"--base-pipeline-dir={test.dirname}",
        test
    )
    passed, skipped, failed = result.listoutcomes()

    assert len(passed) == 2
    assert len(skipped) == 0
    assert len(failed) == 0


MOCK_PIPELINE_TIMEOUT = """
#!/usr/bin/env python

if __name__ == "__main__":

    import time
    time.sleep(10)
"""


TEST_TIMEOUT = f"""
import os, shutil, unittest

import pytest

from pytest_pipeline import PipelineRun, mark


class MyRun(PipelineRun):

    @mark.before_run
    def test_and_prep_executable(self):
        shutil.copy2("../pipeline", "pipeline")
        assert os.path.exists("pipeline")


run = PipelineRun.make_fixture(
    "class",
    cmd="{sys.executable} pipeline",
    timeout=0.01,
)


@pytest.mark.usefixtures("run")
class TestMyPipeline(unittest.TestCase):

    def test_exit_code(self):
        assert self.run_fixture.exit_code != 0
"""


@pytest.fixture(scope="function")
def mockpipe_timeout(request, testdir):
    """Mock pipeline script with timeout"""
    mp = testdir.makefile("", pipeline=MOCK_PIPELINE_TIMEOUT)
    return mp


def test_pipeline_timeout(mockpipe_timeout, testdir):
    """Test for execution with timeout"""
    test = testdir.makepyfile(TEST_TIMEOUT)
    result = testdir.inline_run(
        "-v",
        f"--base-pipeline-dir={test.dirname}",
        test
    )
    passed, skipped, failed = result.listoutcomes()

    assert len(passed) == 0
    assert len(skipped) == 0
    assert len(failed) == 1


MOCK_PIPELINE_FMT = """
#!/usr/bin/env python

import sys

if __name__ == "__main__":

    print(sys.argv[1])
"""


TEST_FMT = f"""
import os, shutil, unittest

import pytest

from pytest_pipeline import PipelineRun, mark


class MyRun(PipelineRun):

    @mark.before_run
    def prep_executable(self):
        shutil.copy2("../pipeline", "pipeline")
        assert os.path.exists("pipeline")


run = MyRun.make_fixture(
    "class",
    "{sys.executable} pipeline {{run_dir}}",
    stdout=True,
)


@pytest.mark.usefixtures("run")
class TestMyPipeline(unittest.TestCase):

    def test_exit_code(self):
        assert self.run_fixture.exit_code == 0

    def test_stdout(self):
        stdout = self.run_fixture.stdout.decode("utf-8").strip()
        assert self.run_fixture.run_dir == stdout
"""


@pytest.fixture(scope="function")
def mockpipe_fmt(request, testdir):
    """Mock pipeline script with timeout"""
    mp = testdir.makefile("", pipeline=MOCK_PIPELINE_FMT)
    return mp


def test_pipeline_fmt(mockpipe_fmt, testdir):
    """Test for run with templated command"""
    test = testdir.makepyfile(TEST_FMT)
    result = testdir.inline_run(
        "-v",
        f"--base-pipeline-dir={test.dirname}",
        test
    )
    passed, skipped, failed = result.listoutcomes()

    assert len(passed) == 2
    assert len(skipped) == 0
    assert len(failed) == 0
