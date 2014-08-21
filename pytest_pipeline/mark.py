# -*- coding: utf-8 -*-
"""
    pytest_pipeline.mark
    ~~~~~~~~~~~~~~~~~~~~

    Marks for pipeline run tests.

    :copyright: (c) 2014 Wibowo Arindrarto <bow@bow.web.id>
    :license: BSD

"""

from functools import wraps


UNMARKED = -1
BEFORE_RUN = 0
IN_RUN = 1
AFTER_RUN = 2


# TODO: implement ordering in before_run and after_run

def before_run(func):
    func._pipeline = {"phase": BEFORE_RUN}
    @wraps(func)
    def wrapped(self, *args, **kwargs):
        return func(self, *args, **kwargs)
    return wrapped


def after_run(func):
    func._pipeline = {"phase": AFTER_RUN}
    @wraps(func)
    def wrapped(self, *args, **kwargs):
        if self.pipeline_run.exit_code is None:
            # TODO: can we provide a more informative traceback if the this
            #       subprocess run fails?
            self._run_before_run_methods()
            self.pipeline_run.launch_process_and_wait()
        return func(self, *args, **kwargs)
    return wrapped


