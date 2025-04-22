
# ECU Audit CLI + Web Viewer

A secure audit logging system for vehicle ECUs over CAN (ELM327) with a minimal web-based dashboard.

## Features
- 🔒 Secure log generation with HMAC-SHA256
- 🛠 Connects via ELM327 over USB serial
- 📊 Web dashboard to view and search logs
- 📦 CLI support for custom log size, secrets, and export path
- 🐳 Dockerized setup
- 🧪 GitHub Actions CI for validation

## Installation
```bash
pip install -e .
```

## Usage
```bash
ecu-audit --channel COM3 --dump logs.json --secret myKey --buffer 100
```

## Run Web Viewer
```bash
python ecu_audit/webapp.py
```
Visit [http://localhost:5000](http://localhost:5000)

## Build & Run with Docker
```bash
docker build -t ecu-audit .
docker run -p 5000:5000 ecu-audit
```

## Continuous Integration
GitHub Actions will auto-check Python packaging and run your tests.

## License
MIT
