import logging
import os
from logging.handlers import RotatingFileHandler
from flask import Flask, request, jsonify
from tcl_helper import init_tcl, eval_cmd, get_tcl

# Configure logger for the server
LOG_DIR = os.path.join(os.path.dirname(__file__), "logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "server.log")

logger = logging.getLogger("hlt_server")
if not logger.handlers:
    logger.setLevel(logging.INFO)
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
    init_tcl()
    return jsonify(message="Tcl package initialized")


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
    result = eval_cmd(command)
    return jsonify(message=f"Executing {command}", result=result)


if __name__ == "__main__":
    # Start the Flask server on port 8000
    logger.info("Starting server on 0.0.0.0:8000")
    app.run(host="0.0.0.0", port=8000)
