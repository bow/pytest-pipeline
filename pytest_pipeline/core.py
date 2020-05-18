# -*- coding: utf-8 -*-
"""
    pytest_pipeline.core
    ~~~~~~~~~~~~~~~~~~~~

    Core pipeline test classes.

"""
# (c) 2014-2020 Wibowo Arindrarto <bow@bow.web.id>

import inspect
import os
import shlex
import shutil
import subprocess
import tempfile
import threading
import time
from uuid import uuid4

import pytest


# TODO: allow multiple runs to be executed in test pipelines
class PipelineRun:

    def __init__(
        self,
        cmd,
        stdout=None,
        stderr=None,
        poll_time=0.01,
        timeout=None,
    ):
        self.cmd = cmd
        self.stdout = stdout
        self.stderr = stderr
        self.poll_time = poll_time
        self.timeout = float(timeout) if timeout is not None else timeout
        self._process = None
        # set by the make_fixture functions at runtime
        self.run_dir = None

    def __repr__(self):
        return f"{self.__class__.__name__}(run_id={self.run_id}, ...)"

    def __launch_main_process(self):

        if isinstance(self.stdout, str):
            self.stdout = open(self.stdout, "w")
        elif self.stdout is None:
            self.stdout = open(os.devnull, "w")
        elif self.stdout is True:
            self.stdout = subprocess.PIPE

        if isinstance(self.stderr, str):
            self.stderr = open(self.stderr, "w")
        elif self.stderr is None:
            self.stderr = open(os.devnull, "w")
        elif self.stderr is True:
            self.stderr = subprocess.PIPE

        def target():
            toks = shlex.split(
                self.cmd.format(run_dir="'" + self.run_dir + "'")
            )
            self._process = subprocess.Popen(
                toks,
                stdout=self.stdout,
                stderr=self.stderr,
            )
            while self._process.poll() is None:
                time.sleep(self.poll_time)

        thread = threading.Thread(target=target)
        thread.start()

        thread.join(self.timeout)
        if thread.is_alive():
            self._process.terminate()
            pytest.fail(f"Process is taking longer than {self.timeout} seconds")

        if self.stdout == subprocess.PIPE:
            self.stdout = self._process.stdout.read()
        if self.stderr == subprocess.PIPE:
            self.stderr = self._process.stderr.read()

        return None

    @classmethod
    def _get_before_run_funcs(cls):
        funcs = []

        def pred(obj):
            return hasattr(obj, "_before_run_order")

        for _, func in inspect.getmembers(cls, predicate=pred):
            funcs.append(func)

        return sorted(funcs, key=lambda f: getattr(f, "_before_run_order"))

    @classmethod
    def class_fixture(cls, *args, **kwargs):
        return cls.make_fixture("class", *args, **kwargs)

    @classmethod
    def make_fixture(cls, scope, *args, **kwargs):

        @pytest.fixture(scope=scope)
        def fixture(request):
            run = cls(*args, **kwargs)

            init_dir = os.getcwd()
            # create base pipeline dir if it does not exist
            root_test_dir = request.config.option.base_pipeline_dir
            if root_test_dir is None:
                root_test_dir = os.path.join(
                    tempfile.gettempdir(),
                    "pipeline_tests",
                )
                if not os.path.exists(root_test_dir):
                    os.makedirs(root_test_dir)
            test_dir = os.path.join(root_test_dir, run.run_id)
            run.run_dir = test_dir
            # warn if we are removing existing directory?
            if os.path.exists(test_dir):
                shutil.rmtree
            os.makedirs(test_dir)

            def done():
                os.chdir(init_dir)

            request.addfinalizer(done)

            os.chdir(test_dir)
            for func in cls._get_before_run_funcs():
                func(run)

            run.__launch_main_process()

            if scope != "class":
                return run

            request.cls.run_fixture = run

        return fixture

    @property
    def run_id(self):
        if not hasattr(self, "_run_id"):
            self._run_id = f"{self.__class__.__name__}_{uuid4()}"

        return self._run_id

    @property
    def exit_code(self):
        if self._process is not None:
            return self._process.returncode

        return None
