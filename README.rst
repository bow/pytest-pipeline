===============================
pytest-pipeline
===============================

.. image:: https://badge.fury.io/py/pytest-pipeline.svg
        :target: http://badge.fury.io/py/pytest-pipeline

.. image:: https://travis-ci.org/bow/pytest-pipeline.png?branch=master
        :target: https://travis-ci.org/bow/pytest-pipeline

pytest-pipeline is a Python3-compatible pytest plugin for functional testing
of data analysis pipelines. They are usually long-running scripts or executables
with multiple input and/or output files + directories.

It is meant for end-to-end testing where you test for conditions before the
pipeline run and after the pipeline runs (output files, checksums, etc.).


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
    from pytest_pipeline import PipelineRun, PipelineTest, mark, utils

    # one pipeline run is represented by one class that subclasses PipelineTest
    class TestMyPipeline(PipelineTest):

        # define the pipeline execution via PipelineRun objects
        run = PipelineRun(
            # the actual command to start your pipeline
            cmd="./run_pipeline",
            stdout="run.stdout",
        )

        # before_run-marked functions will be run before the pipeline is executed
        @mark.before_run
        def test_prep_executable(self):
            # copy the executable to the run directory
            shutil.copy2("/path/to/run_pipeline", "run_pipeline")
            # testing if the file is executable
            assert os.access("run_pipeline", os.X_OK)

        # after_run-marked tests will only be run after pipeline execution is finished
        @mark.after_run(order=1)
        def test_result_md5(self):
            assert utils.file_md5sum("result.txt") == "50a2fabfdd276f573ff97ace8b11c5f4"

        # ordering for all tests annotated by after_run can be set manually
        # here we want to test the exit code first after the run is finished
        @mark.after_run(order=0)
        def test_exit_code(self):
            assert self.run.exit_code == 0

        # we can also check the stdout that we capture as well
        @mark.after_run(order=2)
        def test_stdout(self):
            assert open("run.stdout", "r").read().strip() == "Result computed"

If the test above is saved as ``test_demo.py``, you can then run the test by
executing ``py.test -v test_demo.py``. You should see that four tests were
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
  called ``run.stdout`` as well. For long running pipelines, you can also supply
  a ``timeout`` argument which limits how long the pipeline process can run.

- Test ordering.
  Pipelines by definition are simply series of commands executed subsequently.
  The plugin allows you to also order your tests accordingly via the
  ``before_run`` and ``after_run`` decorators. In the code above, we first test
  for the exit code before testing the output files. Using the command line flag
  ``--xfail-pipeline``, if the first test after the pipeline run fails then
  the rest will be marked as failed immediately.

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
