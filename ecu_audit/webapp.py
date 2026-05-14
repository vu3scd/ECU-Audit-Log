
from flask import Flask, render_template, jsonify, request
import json
import os

# Resolve templates relative to the repo root so the app works no matter
# which directory it is launched from. webapp.py lives in ecu_audit/, so the
# repo root is one level up, and templates/ sits there.
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_TEMPLATE_DIR = os.path.join(_REPO_ROOT, 'templates')

app = Flask(__name__, template_folder=_TEMPLATE_DIR)

# Log file is resolved relative to the repo root too, for the same reason.
LOG_PATH = os.path.join(_REPO_ROOT, 'ecu_audit_logs.json')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/logs')
def get_logs():
    if not os.path.exists(LOG_PATH):
        return jsonify([])
    with open(LOG_PATH, 'r') as f:
        logs = json.load(f)
    return jsonify(logs)


# --- Adapter capability check --------------------------------------------

@app.route('/capabilities')
def capabilities_page():
    """Page where the user can probe a connected ELM327 adapter."""
    return render_template('capabilities.html')


@app.route('/api/devices')
def api_devices():
    """List serial ports that look like ELM327 / OBD adapters."""
    try:
        from utils.device_detection import detect_elm327_ports
    except ImportError as e:
        return jsonify({"error": f"Device detection unavailable: {e}",
                        "devices": []}), 500
    try:
        ports = detect_elm327_ports()
    except Exception as e:
        return jsonify({"error": f"Could not list serial ports: {e}",
                        "devices": []}), 500
    return jsonify({
        "error": None,
        "devices": [{"port": p, "description": d} for p, d in ports],
    })


@app.route('/api/probe')
def api_probe():
    """Run the read-only capability probe against a chosen serial port.

    Query param: ?port=/dev/cu.XXXX  (required)

    This is synchronous: the request blocks while the probe talks to the
    adapter (typically a few seconds), then returns the structured result.
    """
    port = request.args.get('port', '').strip()
    if not port:
        return jsonify({"error": "missing required 'port' query parameter"}), 400

    try:
        from ecu_audit.elm327 import probe_capabilities
    except ImportError as e:
        return jsonify({"error": f"ELM327 module unavailable: {e}"}), 500

    # probe_capabilities is designed never to raise for comms problems --
    # it returns the failure inside the result dict.
    result = probe_capabilities(port)
    return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True)
