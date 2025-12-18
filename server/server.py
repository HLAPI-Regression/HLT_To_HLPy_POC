from flask import Flask, request, jsonify
from tcl_helper import init_tcl, eval_cmd, get_tcl

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
    print("Executing command:", command)
    result = eval_cmd(command)
    return jsonify(message=f"Executing {command}", result=result)


if __name__ == "__main__":
    # Start the Flask server on port 8000
    app.run(host="0.0.0.0", port=8000)
