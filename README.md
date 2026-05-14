
# ECU Audit CLI + Web Viewer

![Python](https://img.shields.io/badge/Python-3.7%2B-green?logo=python)
![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20Windows%20%7C%20macOS-blue)
![Docker](https://img.shields.io/badge/Docker-Supported-blue?logo=docker)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

A CLI + web-based audit logger for vehicle ECUs, built around ELM327 over CAN.
The focus is **tamper-evident logging**: events are recorded into a
cryptographically chained log so that later edits, deletions, or reordering
can be detected.

> **Project status: pre-release / proof-of-concept.**
> The secure logging core is implemented and tested. Live ECU communication
> over CAN is **not yet implemented** — see [Roadmap](#roadmap) below for an
> honest breakdown of what works today versus what is planned.

---

## What works today

| Capability | Status |
|---|---|
| Hash-chained, HMAC-signed event logging | ✅ Implemented & unit-tested |
| Integrity verification (`verify_logs` / `--verify`) | ✅ Implemented & unit-tested |
| ELM327 / OBD serial device **detection** | ✅ Implemented |
| Flask web viewer for browsing logs | ✅ Implemented |
| Live CAN frame reading from a vehicle | ❌ Not yet implemented |
| UDS diagnostic requests (`0x19`, `0x22`) | ❌ Planned (v0.3) |
| CBOR / AUTOSAR XML export | ❌ Planned (v0.3) |

In other words: the tool can **create, sign, store, and verify** an audit log
today, and can **detect** a connected ELM327 adapter — but it does not yet
**read traffic** from a vehicle. The `--auto` command currently detects a
device and writes a session-start event; the CAN read loop is the next
milestone.

---

## How the tamper-evident log works

Each log entry contains:

| Field | Meaning |
|---|---|
| `prev_sig` | Signature of the preceding entry (`GENESIS` for the first) |
| `timestamp` | UTC ISO-8601 time the event was recorded |
| `event_id` | Integer event identifier |
| `severity` | Integer severity level |
| `module` | Source module / subsystem |
| `message` | Human-readable description |
| `signature` | HMAC-SHA256 over the canonical form of all fields above |

Because `prev_sig` is part of the **signed** payload, every entry is
cryptographically bound to its predecessor, transitively back to a fixed
genesis marker. `verify_logs()` therefore detects:

- **field edits** — the modified entry's own signature no longer matches
- **deletions** — the following entry's `prev_sig` link is broken
- **reordering** — the `prev_sig` links no longer line up

**Important:** the guarantee only holds if the signing key is kept somewhere
the audited system cannot reach. Anyone with both the log and the key can
re-sign a modified log. Supply the key via `--secret-key` or the
`ECU_AUDIT_KEY` environment variable.

---

## Quick Start

```bash
pip install -r requirements.txt
```

**Run the web viewer** (browse an existing log file):

```bash
python ecu_audit/webapp.py
# then open http://localhost:5000
```

**Detect a device and start a logging session:**

```bash
export ECU_AUDIT_KEY="your-signing-key"
ecu-audit --auto
```

**Verify the integrity of a log file:**

```bash
ecu-audit --verify --secret-key "your-signing-key"
```

This exits `0` if the chain is intact, or non-zero and prints the failing
entry indices if it is not.

---

## Linux USB access

Detecting a USB ELM327 adapter on Linux usually requires serial port
permissions:

```bash
sudo usermod -aG dialout $USER   # then log out and back in
```

Python ≥ 3.7 is required.

---

## Running the tests

```bash
python -m unittest discover -s tests -v
```

The test suite covers entry creation, chain linkage, persistence, and the
three tamper scenarios above.

---

## Roadmap

| Version | Focus | State |
|---|---|---|
| v0.1 | CLI logging skeleton, Flask viewer, Docker | Done |
| v0.2 | Hash-chained tamper-evident logging, device detection, tests | **Current** |
| v0.3 | Live CAN read loop, UDS requests, CBOR/XML export | Planned |
| v0.4 | Multi-ECU gateway mode, cloud/MQTT forwarding | Planned |
| v1.0 | Access control, ISO/UNR mapping docs, chain-of-custody reports | Planned |

References to ISO/SAE 21434 and UN R155/R156 describe the **intended**
direction of the project. They are design goals, not claims of certification
or compliance.

---

## License

MIT © 2025 Sumit Chouhan
