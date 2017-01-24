pytest-pipeline
===============

|ci| |coverage| |pypi|

.. |ci| image:: https://travis-ci.org/bow/pytest-pipeline.png?branch=master
        :target: https://travis-ci.org/bow/pytest-pipeline

.. |coverage| image:: https://codecov.io/gh/bow/pytest-pipeline/branch/master/graph/badge.svg
        :target: https://codecov.io/gh/bow/pytest-pipeline

.. |pypi| image:: https://badge.fury.io/py/pytest-pipeline.svg
        :target: http://badge.fury.io/py/pytest-pipeline


pytest-pipeline is a pytest plugin for functional testing of data analysis
pipelines. They are usually long-running scripts or executables with multiple
input and/or output files + directories. The plugin is meant for end-to-end
testing where you test for conditions before the pipeline run and after the
pipeline runs (output files, checksums, etc.).

pytest-pipeline is tested against Python versions 2.7, 3.3, 3.4, 3.5, and 3.6.


Installation
============

::

    pip install pytest-pipeline


Walkthrough
===========

For our example, we will use a super simple pipeline that writes a file and
prints to stdout:

.. code-block:: python

    #!/usr/bin/env python

    from __future__ import print_function

    if __name__ == "__main__":

        with open("result.txt", "w") as result:
            result.write("42\n")
        print("Result computed")

At this point it's just a simple script, but it should be enough to illustrate
the plugin. Also, if you want to follow along, save the above file as
``run_pipeline``.

With the pipeline above, here's how your test would look like with
``pytest_pipeline``:

.. code-block:: python

    import os
    import shutil
    import unittest
    from pytest_pipeline import PipelineRun, mark, utils

    # we can subclass `PipelineRun` to add custom methods
    # using `PipelineRun` as-is is also possible
    class MyRun(PipelineRun):

        # before_run-marked functions will be run before the pipeline is executed
        @mark.before_run
        def test_prep_executable(self):
            # copy the executable to the run directory
            shutil.copy2("/path/to/run_pipeline", "run_pipeline")
            # ensure that the file is executable
            assert os.access("run_pipeline", os.X_OK)

    # a pipeline run is treated as a test fixture
    run = MyRun.class_fixture(cmd="./run_pipeline", stdout="run.stdout")

    # the fixture is bound to a unittest.TestCase using the usefixtures mark
    @pytest.mark.usefixtures("run")
    # tests per-pipeline run are grouped in one unittest.TestCase instance
    class TestMyPipeline(unittest.TestCase):

        def test_result_md5(self):
            assert utils.file_md5sum("result.txt") == "50a2fabfdd276f573ff97ace8b11c5f4"

        def test_exit_code(self):
            # the run fixture is stored as the `run_fixture` attribute
            assert self.run_fixture.exit_code == 0

        # we can check the stdout that we capture as well
        def test_stdout(self):
            assert open("run.stdout", "r").read().strip() == "Result computed"

If the test above is saved as ``test_demo.py``, you can then run the test by
executing ``py.test -v test_demo.py``. You should see that three tests were
executed and all four passed.

What just happened?
-------------------

You just executed your first pipeline test. The plugin itself gives you:

- Test directory creation (one class gets one directory).
  By default, testdirectories are all created in the ``/tmp/pipeline_test``
  directory. You can tweak this location by supplying the
  ``--base-pipeline-dir`` command line flag.

- Automatic execution of the pipeline.
  No need to ``import subprocess``, just define the command via the
  ``PipelineRun`` object. We optionally captured the standard output to a file
  called ``run.stdout``. Not a fan of doing disk IO? You can also set ``stdout``
  and/or ``stderr`` to ``True`` and have their values captured in-memory.

- Timeout control.
  For long running pipelines, you can also supply a ``timeout`` argument which
  limits how long the pipeline process can run.

And since this is a py.test plugin, test discovery and execution is done via
py.test.


Getting + giving help
=====================

Please use the `issue tracker <https://github.com/bow/pytest-pipeline/issues>`_
to report bugs or feature requests. You can always fork and submit a pull
request as well.


License
=======

See LICENSE.
