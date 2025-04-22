
from flask import Flask, render_template, request, jsonify
import json
import os

app = Flask(__name__)

LOG_PATH = 'ecu_audit_logs.json'

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

if __name__ == '__main__':
    app.run(debug=True)
