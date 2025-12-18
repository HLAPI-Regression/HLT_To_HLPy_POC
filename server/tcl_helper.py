import sys, os
import threading
from tkinter import Tcl, TclError

# Global singleton Tcl interpreter + lock for thread-safe init
_global_lock = threading.Lock()
_global_tcl = None


def init_tcl():
    """Initialize and return the global Tcl interpreter (idempotent).

    This will create the `Tcl()` instance once and call any required
    package initialization (e.g. `package require Ixia`).
    """
    global _global_tcl
    with _global_lock:
        if _global_tcl is None:
            _global_tcl = Tcl()
            try:
                _global_tcl.eval("package require Ixia")
            except TclError:
                raise
    return _global_tcl


def get_tcl():
    """Return the global Tcl interpreter, initializing if necessary."""
    global _global_tcl
    if _global_tcl is None:
        return init_tcl()
    return _global_tcl


def eval_cmd(cmd) -> str:
    """Eval a Tcl command and return its result.

    Accepts either `eval_cmd(cmd)` — which uses the global interpreter —
    or `eval_cmd(tcl, cmd)` for callers that pass an explicit Tcl instance.
    """
    tcl = get_tcl()

    try:
        result = tcl.eval(cmd)
        return result
    except TclError:
        raise