# -*- coding: utf-8 -*-
"""
    pytest_pipeline.core
    ~~~~~~~~~~~~~~~~~~~~

    Core pipeline test classes.

    :copyright: (c) 2014 Wibowo Arindrarto <bow@bow.web.id>
    :license: BSD

"""

import os
import shlex
import subprocess
import threading
import time
from uuid import uuid4

import pytest
from past.builtins import basestring
from future.utils import iteritems, with_metaclass


#TODO: allow multiple runs to be executed in test pipelines

class PipelineRun(object):

    def __init__(self, cmd, stdout=None, stderr=None,
                 poll_time=0.01, timeout=None):
        self.cmd = cmd
        self.stdout = stdout
        self.stderr = stderr
        self.poll_time = poll_time
        self.timeout = float(timeout) if timeout is not None else timeout
        self._process = None
        self._toks = shlex.split(cmd)

    def __repr__(self):
        return "{0}(...)".format(self.__class__.__name__)

    @property
    def run_id(self):
        if not hasattr(self, "_run_id"):
            self._run_id = str(uuid4())
        return self._run_id

    @property
    def exit_code(self):
        if self._process is not None:
            return self._process.returncode

    def launch_process_and_wait(self):

        def target():
            self._process = subprocess.Popen(self._toks, stdout=self.stdout,
                                             stderr=self.stderr)
            while self._process.poll() is None:
                time.sleep(self.poll_time)

        if isinstance(self.stdout, basestring):
            self.stdout = open(self.stdout, "w")
        elif self.stdout is None:
            self.stdout = open(os.devnull, "w")

        if isinstance(self.stderr, basestring):
            self.stderr = open(self.stderr, "w")
        elif self.stderr is None:
            self.stderr = open(os.devnull, "w")

        thread = threading.Thread(target=target)
        thread.start()

        thread.join(self.timeout)
        if thread.is_alive():
            self._process.terminate()
            pytest.fail("Process is taking longer than {0} seconds".format(self.timeout))


class MetaPipelineTest(type):

    def __new__(meta, name, bases, dct):
        # ensure that only subclasses of PipelineTest has the custom __new__
        # and not PipelineTest itself
        if not [base for base in bases if isinstance(base, MetaPipelineTest)]:
            return super(MetaPipelineTest, meta).__new__(meta, name, bases, dct)

        for attr, val in iteritems(dct):

            if attr == "run" and not isinstance(val, PipelineRun):
                raise ValueError("Test class '{0}' does not have a proper "
                                 "'run' attribute".format(meta))

            if not callable(val) or not hasattr(val, "_pipeline"):
                continue

            if "run" not in dct:
                dct[attr] = pytest.mark.skipif(True, reason="Pipeline marked noexec")(val)

            dct[attr] = pytest.mark.xfail_pipeline(val)

        return super(MetaPipelineTest, meta).__new__(meta, name, bases, dct)

    def __init__(cls, name, bases, dct):
        # only create test fixtures if there is a run attribute
        if "run" in dct:
            cls.test_id = str(uuid4())
            cls.test_dirname = cls.__name__ + "_" + cls.test_id
            cls = pytest.mark.usefixtures("_autogendir")(cls)
            super(MetaPipelineTest, cls).__init__(name, bases, dct)


class PipelineTest(with_metaclass(MetaPipelineTest)):

    def __repr__(self):
        return "{0}(id='{1}', ...)".format(self.__class__.__name__, self.test_id)
