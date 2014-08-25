===============================
pytest-pipeline
===============================

pytest-pipeline is a pytest plugin for functional testing of data analysis
pipelines.

It is meant for end-to-end testing where you test for conditions before the
pipeline run and after the pipeline runs (output files, checksums, etc.)

The Code
========

Here's how your test would look like with ``pytest_pipelines``:

.. code-block:: python

    import os
    from pytest_pipeline import PipelineRun, PipelineTest, mark, utils

    # one pipeline run is represented by one class that subclasses PipelineTest
    class TestMyPipeline(PipelineTest):

        # define the pipeline execution via PipelineRun objects
        run = PipelineRun(
            # the actual command to start your pipeline
            cmd="./run_pipeline",
            # capture stdout to a file (only when --capture=no is set in py.test)
            stdout="run.stdout",
        )

        # before_run-marked functions will be run before the pipeline is executed
        @mark.before_run
        def prep_executable(self):
            # here we will create a symlink in the test directory
            # pointing to /usr/bin/pipeline
            # by default, each Test class gets its own run directory
            os.symlink("/usr/bin/pipeline", "run_pipeline")

        # you can run tests with before_run too
        @mark.before_run
        def test_env_vars(self):
            assert "MY_VAR" in os.environ

        # after_run-marked tests will only be run after pipeline execution is finished
        @mark.after_run
        def test_a_file(self):
            assert utils.file_md5sum("file.txt") == "68ba00eb6995aeecb19773a27bf81b3d"

        # ordering for all tests annotated by after_run can be set manually
        # here we want to test the exit code first after the run is finished
        @mark.after_run(order=0)
        def test_exit_code(self):
            assert self.run.exit_code == 0

        # this test will be run after the test above
        @mark.after_run(order=1)
        def test_another_file(self):
            assert "result" in open("another_file.txt").read()

        # you can also still define standalone tests, discoverable by py.test
        def test_standalone(self):
            assert 1 == 1

With the code above, you get:

- Test directory creation (one class gets one directory)
- Tests before and after the pipeline run ordered properly

Optionally:

- stdout and stderr redirection (if ``--capture=no`` is set)
- test execution halt as soon as any ``before_run`` or the actual pipeline run
  fails (if ``--xfail-pipeline`` is set)

And since this is a py.test plugin, test discovery and execution is done via
py.test.


Why ....
========

... did you make this?
----------------------

I feel like writing pipeline tests using the currently-available libraries
is too cumbersome. A lot of the tasks are repetitive (set this directory,
run the pipeline, check the output files, etc.) and I think they should be
better-automated.

... make it a py.test plugin?
-----------------------------
Because py.test is awesome. Plus I don't feel like reinventing the wheel.

... do functional testing?
--------------------------
Because it's the responsible way to develop data analysis pipelines.


LIMITATIONS
===========

- ``after_run`` and ``before_run`` can only be applied to test functions


WARNING
=======

This is alpha software. Things will blow up!
