
# ECU Audit CLI + Web Viewer

![Kali Tested](https://img.shields.io/badge/Kali-2023.1%2B-blueviolet?logo=linux)
![Python](https://img.shields.io/badge/Python-3.10%2B-green?logo=python)
![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20Windows%20%7C%20macOS-blue)
![Docker](https://img.shields.io/badge/Docker-Supported-blue?logo=docker)
![Built with Love](https://img.shields.io/badge/Built%20with-%E2%9D%A4-red)

---

A secure CLI + web-based audit logger for vehicle ECUs using ELM327 over CAN.  
Built for traceability, regulation readiness (UN R155/R156), and usability.

##  v0.2.1 Updates

- ✅ Auto-detects ELM327 or compatible USB/Bluetooth devices
- ✅ CLI probes serial ports and prompts for user selection
- ✅ Verified support for Kali Linux 2023.1+
- ✅ USB access group instructions for Linux

---

## Planned for v0.3.0

- Support UDS requests (`0x19`, `0x22`) for reading diagnostics
- Export logs to CBOR and AUTOSAR XML format
- Secure logging gateway prototype with multi-ECU support
- Integration with ISO 21434 Clause 11/15 requirements
- Optional local SQLite backend for persistence

---

## Linux Support Matrix

| Distro        | Version        | Status    |
|---------------|----------------|-----------|
| Ubuntu        | 20.04+         | ✅         |
| Debian        | 11+            | ✅         |
| Kali Linux    | 2023.1+        | ✅         |
| Arch/Manjaro  | Rolling        | ✅         |
| Fedora/RHEL   | 34+            | 🟡 (USB perms fix)

Python ≥ 3.7 required. Use `sudo usermod -aG dialout $USER` for USB access on Linux.

---

## Quick Start

```bash
pip install -r requirements.txt
python ecu_audit/webapp.py
```

Then visit: http://localhost:5000

```bash
ecu-audit --auto
```

---

## License

MIT © 2025 Sumit Chouhan
