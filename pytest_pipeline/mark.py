# -*- coding: utf-8 -*-
"""
    pytest_pipeline.mark
    ~~~~~~~~~~~~~~~~~~~~

    Marks for pipeline run tests.

    :copyright: (c) 2014 Wibowo Arindrarto <bow@bow.web.id>
    :license: BSD

"""

import sys
from functools import wraps


UNMARKED = -1
BEFORE_RUN = 0
IN_RUN = 1
AFTER_RUN = 2


# trying to emulate Python's builtin argument handling here
# so we can have decorators with optional arguments
def before_run(__firstarg=None, order=sys.maxsize, **kwargz):
    # first case: when decorator has no args
    _pdict = {
        "phase": BEFORE_RUN,
        "order": order,
    }
    # TODO: can we have less duplication here?
    if callable(__firstarg) and len(kwargz) == 0:
        func = __firstarg
        func._pipeline = _pdict
        @wraps(func)
        def wrapped(self, *args, **kwargs):
            return func(self, *args, **kwargs)
        return wrapped
    # other cases: when decorator has args
    elif __firstarg is None:
        def onion(func):       # layers, right?
            func._pipeline = _pdict
            @wraps(func)
            def wrapped(self, *args, **kwargs):
                return func(self, *args, **kwargs)
            return wrapped
        return onion
    # fall through other cases
    else:
        raise ValueError("Decorator 'before_run' set incorrectly")


# see before_run comments
def after_run(__firstarg=None, order=sys.maxsize, **kwargz):
    _pdict = {
        "phase": AFTER_RUN,
        "order": order,
    }
    if callable(__firstarg) and len(kwargz) == 0:
        func = __firstarg
        func._pipeline = _pdict
        @wraps(func)
        def wrapped(self, *args, **kwargs):
            run = getattr(self, "run", None)
            if run is not None:
                if run.exit_code is None:
                    # TODO: can we provide a more informative traceback if the this
                    #       subprocess run fails?
                    self.run.launch_process_and_wait()
            return func(self, *args, **kwargs)
        return wrapped
    elif __firstarg is None:
        def onion(func):
            func._pipeline = _pdict
            @wraps(func)
            def wrapped(self, *args, **kwargs):
                run = getattr(self, "run", None)
                if run is not None:
                    if run.exit_code is None:
                        # TODO: implement properly with after_run counterpart
                        # self._run_before_run_methods()
                        self.run.launch_process_and_wait()
                return func(self, *args, **kwargs)
            return wrapped
        return onion
    else:
        raise ValueError("Decorator 'after_run' set incorrectly")
