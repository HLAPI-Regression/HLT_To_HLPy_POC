import logging
import os
from logging.handlers import RotatingFileHandler
from flask import Flask, request, jsonify
from pyats.tcl import TclError
from tcl_helper import init_tcl, eval_cmd, get_tcl, list_tcl_procs


# Configure logger for the server
LOG_DIR = os.path.join(os.path.dirname(__file__), "logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "server.log")

logger = logging.getLogger("hlt_server")
if not logger.handlers:
    logger.setLevel(logging.DEBUG)
    fmt = logging.Formatter(
        "%(asctime)s %(levelname)-8s %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    # Console handler
    ch = logging.StreamHandler()
    ch.setFormatter(fmt)
    logger.addHandler(ch)
    # Rotating file handler
    fh = RotatingFileHandler(LOG_FILE, maxBytes=10 * 1024 * 1024, backupCount=5)
    fh.setFormatter(fmt)
    logger.addHandler(fh)

app = Flask(__name__)

# Define a root endpoint
@app.route("/", methods=["GET"])
def read_root():
    return jsonify(message="Welcome to the Isolated tcl server")


@app.route("/init", methods=["POST"])
def init():
    try:
        init_tcl()
        return jsonify(message="Tcl package initialized")
    except TclError as e:
        logger.error("TclError during init: %s", e)
        return jsonify(error=f"Tcl error: {str(e)}"), 500
    except Exception as e:
        logger.error("Unexpected error during init: %s", e, exc_info=True)
        return jsonify(error=f"Unexpected error: {str(e)}"), 500


@app.route("/dir", methods=["GET"])
def dir_namespace():
    namespace = request.args.get("namespace")
    if not namespace:
        return jsonify(error="Missing 'namespace' query parameter"), 400
    try:
        procs = list_tcl_procs(namespace)
        return jsonify(namespace=namespace, procs=procs)
    except TclError as e:
        logger.error("TclError listing procs in namespace '%s': %s", namespace, e)
        return jsonify(error=f"Tcl error: {str(e)}"), 500
    except Exception as e:
        logger.error("Unexpected error listing procs: %s", e, exc_info=True)
        return jsonify(error=f"Unexpected error: {str(e)}"), 500


# Define an execute endpoint
@app.route("/execute", methods=["POST"])
def execute():
    data = request.get_json(silent=True) or {}
    command = None
    if isinstance(data, dict):
        command = data.get("command")
    if not command:
        return jsonify(error="Missing 'command' in JSON body, form or query"), 400
    logger.info("Executing command: %s", command)
    try:
        result = eval_cmd(command)
        return jsonify(message=f"Executing {command}", result=result)
    except TclError as e:
        logger.error("TclError executing command '%s': %s", command, e)
        return jsonify(error=f"Tcl error: {str(e)}"), 500
    except Exception as e:
        logger.error("Unexpected error executing command: %s", e, exc_info=True)
        return jsonify(error=f"Unexpected error: {str(e)}"), 500


if __name__ == "__main__":
    # Start the Flask server on port 8000
    logger.info("Starting server on 0.0.0.0:8000")
    app.run(host="0.0.0.0", port=8000)
