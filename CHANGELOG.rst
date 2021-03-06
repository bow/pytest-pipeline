.. :changelog:

Changelog
=========

Version 0.4
-----------

Release 0.4.0
^^^^^^^^^^^^^

Release date: TBD

* Allow for the passed in command to access the run directory name
  via ``{run_dir}``.
* Drop official support for Python 2.7, 3.3, 3.4, and 3.5.
* Drop official support for pytest <5.0.0.


Version 0.3
-----------

Release 0.3.0
^^^^^^^^^^^^^

Release date: 24 January 2017

* Allow stdout and/or stderr capture in-memory. This can be done by
  setting their respective keyword arguments to ``True`` when creating
  the run fixture.


Version 0.2
-----------

Release 0.2.0
^^^^^^^^^^^^^

Release date: 31 March 2015

* Pipeline runs are now modelled differently. Instead of a class attribute,
  they are now created as pytest fixtures. This allows the pipeline runs
  to be used in non-`unittest.TestCase` tests.

* The `after_run` decorator is deprecated.

* The command line flags `--xfail-pipeline` and `--skip-run` are deprecated.


Version 0.1
-----------

Release 0.1.0
^^^^^^^^^^^^^

Release date: 25 August 2014

* First release on PyPI.
