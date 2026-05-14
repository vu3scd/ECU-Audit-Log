# ECU Audit CLI + Web Viewer — Roadmap

_A project by Sumit Chouhan: cybersecurity audit logging and diagnostics for
modern ECUs, using ELM327 over CAN._

References to ISO/SAE 21434 and UN R155/R156 below describe the **intended
direction** of the project. They are design goals — not claims of
certification, compliance, or completed alignment.

---

## Status legend
- [x] Implemented and tested
- [~] Implemented, pending hardware validation
- [ ] Not yet started

---

## v0.1 — MVP
- [x] Flask-based searchable log dashboard
- [x] Docker support
- [x] MIT license
- [ ] CLI logging directly from ECUs via ELM327 + CAN _(detection only so
      far; live CAN reading is not yet implemented — see v0.3)_

## v0.2 — Secure logging core _(current)_
- [x] Hash-chained, HMAC-signed tamper-evident log storage
- [x] Integrity verification (`verify_logs()` / `ecu-audit --verify`)
- [x] `ecu-audit` CLI entry point
- [x] Unit tests for logging and tamper detection
- [x] ELM327 / OBD adapter **detection** (USB and paired Bluetooth)
- [~] Adapter **capability check** with web UI — read-only identity,
      firmware, protocol, and voltage probe
- [ ] Event severity tagging aligned with monitoring-granularity goals
- [ ] Log retention policy

## v0.3 — Live diagnostics & UDS
ISO 21434 Clause 15, UN R156
- [ ] Live CAN frame reading from a connected vehicle
- [ ] UDS log requests (e.g. `0x19`, `0x22`)
- [ ] Log software-update attempts
- [ ] Diagnostic session logs and change tracking
- [ ] Structured log export (CBOR / AUTOSAR XML)

## v0.4 — Gateway mode & forwarding
UN R155 (CSMS), ISO 21177
- [ ] Multi-ECU support (e.g. `0x7E8`, `0x7EA`)
- [ ] Gateway collector aggregating logs from multiple ECUs
- [ ] MQTT or HTTPS transport for exporting logs to a backend

## v1.0 — Production grade
Full ISO/SAE 21434 organizational + validation readiness
- [ ] Link logs to TARA-derived threats
- [ ] Chain-of-custody / integrity reporting built on the hash chain
- [ ] Web UI access control (basic auth or OAuth)
- [ ] ISO/UNR mapping table: what is logged vs. what is required
- [ ] Full documentation and threat-logging guidance

---

## Long-term ideas
- [ ] Real-time CAN anomaly detection (simple IDS)
- [ ] Raspberry Pi + CAN HAT demo rig support
- [ ] Developer API for custom ECU apps to push logs
- [ ] OpenTelemetry support for vehicle-wide observability

---

_This roadmap evolves as the project matures._
