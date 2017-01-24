.. :changelog:

Changelog
---------

v0.3.0 (24 January 2017)
------------------------

* Allow stdout and/or stderr capture in-memory. This can be done by
  setting their respective keyword arguments to ``True`` when creating
  the run fixture.


v0.2.0 (31 March 2015)
----------------------

* Pipeline runs are now modelled differently. Instead of a class attribute,
  they are now created as pytest fixtures. This allows the pipeline runs
  to be used in non-`unittest.TestCase` tests.

* The `after_run` decorator is deprecated.

* The command line flags `--xfail-pipeline` and `--skip-run` are deprecated.


v0.1.0 (25 August 2014)
-----------------------

* First release on PyPI.
