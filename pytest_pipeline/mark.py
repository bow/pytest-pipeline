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


# trying to emulate Python's builtin argument handling here
# so we can have decorators with optional arguments
def before_run(__firstarg=None, order=sys.maxsize, **kwargz):
    # first case: when decorator has no args
    # TODO: can we have less duplication here?
    if callable(__firstarg) and len(kwargz) == 0:
        func = __firstarg
        assert not hasattr(func, "_before_run_order"), \
            "Can not set existing '_before_run_order' attribute"
        func._before_run_order = order
        @wraps(func)
        def wrapped(self, *args, **kwargs):
            return func(self, *args, **kwargs)
        return wrapped
    # other cases: when decorator has args
    elif __firstarg is None:
        def onion(func):       # layers, right?
            assert not hasattr(func, "_before_run_order"), \
                    "Can not set existing '_before_run_order' attribute"
            func._before_run_order = order
            @wraps(func)
            def wrapped(self, *args, **kwargs):
                return func(self, *args, **kwargs)
            return wrapped
        return onion
    # fall through other cases
    else:
        raise ValueError("Decorator 'before_run' set incorrectly")
