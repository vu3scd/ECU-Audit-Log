# Release Notes

## v0.2.2 (current)

### New features
- **Adapter capability check (web UI).** New `/capabilities` page in the
  Flask app. Detects connected ELM327 / OBD adapters and runs a read-only
  probe (identity, firmware, current protocol, connector voltage), then
  shows a structured report of what the adapter claims to support.
  *Status: logic-tested against a simulated adapter; pending validation on
  physical hardware.*
- New `ecu_audit/elm327.py` module: a minimal, defensive, **read-only**
  ELM327 communication layer. Every command it sends is an identity or
  configuration query — nothing is written to the vehicle bus.

### Improvements
- Device detection now matches a wider range of adapter names, including
  Bluetooth adapters and common USB-serial chipsets (FTDI, CH340/CH341).
- Added `list_all_ports()` as a manual fallback when auto-detection finds
  nothing but the user knows an adapter is connected.
- Flask app now resolves its templates and log path relative to the repo
  root, so it runs correctly regardless of the working directory it is
  launched from.
- `auto_select_port()` handles invalid or empty input without crashing.

### Fixes
- `pyserial` was imported by the device-detection code but declared in
  neither `requirements.txt` nor `setup.py`, so `--auto` would fail on a
  clean install. It is now a declared dependency.
- Added `.gitignore` (macOS `.DS_Store`, Python caches, runtime log file).

---

## v0.2.1

### New features
- Hash-chained, HMAC-signed audit logging (`SecureAuditLogger`). Each entry
  embeds the previous entry's signature inside its own signed payload,
  making the log tamper-evident against field edits, deletions, and
  reordering.
- `verify_logs()` and the `ecu-audit --verify` CLI flag for checking the
  integrity of an existing log chain.
- Implemented the `ecu-audit` CLI entry point (`main()`), which the
  packaging metadata already referenced but which did not previously exist.

### Improvements
- Test suite expanded from a single test to cover entry creation, chain
  linkage, persistence, and the tamper-detection scenarios. Tests now use
  isolated temporary files.
- README rewritten to state plainly what is implemented versus planned.
- Corrected `setup.py` version and author metadata.

### Notes
- **Breaking:** the on-disk log format changed (entries now carry a
  `prev_sig` field). Logs written by earlier versions will not verify
  against v0.2.1+. No migration path is provided, as the project is
  pre-release.

---

## v0.2.0

### New features
- ELM327 auto-detection — no manual port entry needed.
- CLI prompts for selection when multiple serial devices are found.

### Internal improvements
- Cross-platform serial detection via pyserial.
- Modularised utility functions.

---

## Planned

See `ROADMAP.md` for the full picture. Near-term focus:
- Hardware validation of the capability check against real adapters.
- Live CAN frame reading (the capability check is the first step toward this).
- UDS diagnostic requests (`0x19`, `0x22`).
- Structured log export (CBOR / AUTOSAR XML).
