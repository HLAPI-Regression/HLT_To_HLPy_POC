import sys, os
import threading
import logging
from tkinter import Tcl, TclError

# Logger for tcl helper; uses the server logger namespace if present
_logger = logging.getLogger("hlt_server.tcl_helper")


def log_debug(msg, *args, **kwargs):
    _logger.debug(msg, *args, **kwargs)


def log_info(msg, *args, **kwargs):
    _logger.info(msg, *args, **kwargs)


def log_warning(msg, *args, **kwargs):
    _logger.warning(msg, *args, **kwargs)


def log_error(msg, *args, **kwargs):
    _logger.error(msg, *args, **kwargs)

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
            log_info("Initializing Tcl interpreter")
            _global_tcl = Tcl()
            try:
                _global_tcl.eval("package require Ixia")
                log_info("Tcl package 'Ixia' required successfully")
            except TclError as e:
                log_error("Failed to require Ixia package: %s", e)
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
    log_debug("Eval command: %s", cmd)

    try:
        result = tcl.eval(cmd)
        log_debug("Eval result: %s", result)
        return result
    except TclError as e:
        log_error("Error evaluating Tcl command '%s': %s", cmd, e)
        raise