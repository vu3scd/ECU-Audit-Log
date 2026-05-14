
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
> The secure logging core is implemented and tested. Adapter detection and a
> read-only capability check are implemented. Live ECU communication over CAN
> is **not yet implemented** — see [Roadmap](#roadmap) for an honest
> breakdown of what works today versus what is planned.

---

## What works today

| Capability | Status |
|---|---|
| Hash-chained, HMAC-signed event logging | Implemented & unit-tested |
| Integrity verification (`verify_logs` / `--verify`) | Implemented & unit-tested |
| ELM327 / OBD serial device **detection** (USB & paired Bluetooth) | Implemented |
| Adapter **capability check** (read-only probe, web UI) | Implemented; pending hardware validation |
| Flask web viewer for browsing logs | Implemented |
| Live CAN frame reading from a vehicle | Not yet implemented |
| UDS diagnostic requests (`0x19`, `0x22`) | Planned (v0.3) |
| CBOR / AUTOSAR XML export | Planned (v0.3) |

The tool can **create, sign, store, and verify** an audit log today, and can
**detect and probe** a connected ELM327 adapter. It does not yet **read
traffic** from a vehicle. The capability check is the first step toward that:
it talks to the adapter (read-only) but not to the vehicle bus.

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

## Adapter capability check

"ELM327" is a spec with many clone implementations, and they vary in which
protocols and commands they actually support. The capability check helps a
user answer: *will this adapter do what I expect?*

Open the web viewer and go to **`/capabilities`**. Select a detected adapter
and click **Run Check**. The tool sends a short sequence of **read-only**
commands (identity, firmware, current protocol, connector voltage) and shows
a report of what the adapter reports back.

Notes and limitations:
- Every command sent is read-only. Nothing is written to the vehicle bus, so
  it is safe to run with the ignition on.
- The report shows what the adapter **claims**. A clone may report support
  for something and still behave differently in practice.
- Protocol detection only returns a meaningful value when the adapter is
  connected to a powered vehicle bus.
- A Bluetooth adapter must be paired at the OS level first, so that it is
  exposed as a serial device. If a connected adapter is not detected, it is
  almost certainly a naming gap — the port can still be probed by selecting
  it manually.

---

## Quick Start

```bash
pip install -r requirements.txt
```

**Run the web viewer:**

```bash
python ecu_audit/webapp.py
# logs:          http://localhost:5000
# capability check: http://localhost:5000/capabilities
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

Exits `0` if the chain is intact, or non-zero (printing the failing entry
indices) if it is not.

---

## Linux / macOS adapter access

- **Linux USB:** serial access usually needs group membership —
  `sudo usermod -aG dialout $USER`, then log out and back in.
- **macOS Bluetooth:** pair the adapter in System Settings → Bluetooth first.
  It then appears as a `/dev/cu.*` serial device.

Python ≥ 3.7 is required.

---

## Running the tests

```bash
python -m unittest discover -s tests -v
```

The suite covers entry creation, chain linkage, persistence, and the tamper
scenarios (edit, delete, reorder, wrong key, forged append).

---

## Roadmap

| Version | Focus | State |
|---|---|---|
| v0.1 | CLI/Flask skeleton, Docker | Done |
| v0.2 | Hash-chained logging, device detection, capability check, tests | **Current** |
| v0.3 | Live CAN read loop, UDS requests, CBOR/XML export | Planned |
| v0.4 | Multi-ECU gateway mode, cloud/MQTT forwarding | Planned |
| v1.0 | Access control, ISO/UNR mapping docs, chain-of-custody reports | Planned |

See `ROADMAP.md` for detail and `RELEASE-NOTES.md` for version history.
References to ISO/SAE 21434 and UN R155/R156 describe intended direction, not
certification or compliance.

---

## License

MIT © 2025 Sumit Chouhan
