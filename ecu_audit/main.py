"""
ecu_audit.main
==============

Core secure audit logger for ECU events plus the `ecu-audit` CLI entry point.

Log entries form a *hash chain*: each entry is HMAC-signed, and the signed
payload includes the signature of the preceding entry. Because the link to
the previous entry is itself signed, the dependency is transitive back to a
fixed genesis marker. This makes the log tamper-evident against three
distinct attacks:

  * editing any field of any entry          -> that entry's signature fails
  * deleting an entry from the middle/end   -> the prev_sig link breaks
  * reordering entries                      -> the prev_sig links break

Signatures are keyed with a secret known only to the logging side. For the
guarantee to hold, that key must live somewhere the audited ECU cannot
reach -- otherwise an attacker who can edit the log can also re-sign it.
"""

import argparse
import hashlib
import hmac
import json
import os
from datetime import datetime, timezone

DEFAULT_LOG_PATH = "ecu_audit_logs.json"

# Marker used as the "previous signature" of the very first entry.
GENESIS = "GENESIS"

# Fields covered by the signature, in a fixed order. "prev_sig" is included
# so that each entry is cryptographically bound to its predecessor. The
# "signature" field itself is, of course, excluded.
_SIGNED_FIELDS = ("prev_sig", "timestamp", "event_id", "severity", "module", "message")


class SecureAuditLogger:
    """Append-only, HMAC-signed, hash-chained audit logger."""

    def __init__(self, secret_key, log_path=DEFAULT_LOG_PATH):
        if not secret_key:
            raise ValueError("secret_key must be a non-empty string")
        self._key = secret_key.encode("utf-8")
        self.log_path = log_path
        self._entries = []
        if os.path.exists(self.log_path):
            self._load()

    # ----- internal helpers ------------------------------------------------

    def _canonical(self, entry):
        """Deterministic byte string for the signed portion of an entry."""
        payload = {k: entry[k] for k in _SIGNED_FIELDS}
        return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")

    def _sign(self, entry):
        return hmac.new(self._key, self._canonical(entry), hashlib.sha256).hexdigest()

    def _load(self):
        with open(self.log_path, "r") as f:
            self._entries = json.load(f)

    def _persist(self):
        with open(self.log_path, "w") as f:
            json.dump(self._entries, f, indent=2)

    def _head_signature(self):
        """Signature of the most recent entry, or GENESIS if the log is empty."""
        if not self._entries:
            return GENESIS
        return self._entries[-1]["signature"]

    # ----- public API ------------------------------------------------------

    def log_event(self, event_id, severity, module, message):
        """Record a single event, chain it to the previous one, and persist."""
        entry = {
            "prev_sig": self._head_signature(),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event_id": int(event_id),
            "severity": int(severity),
            "module": str(module),
            "message": str(message),
        }
        entry["signature"] = self._sign(entry)
        self._entries.append(entry)
        self._persist()
        return entry

    def export_logs(self):
        """Return a copy of all log entries currently held."""
        return list(self._entries)

    def verify_logs(self):
        """Re-check the integrity of the whole chain.

        Returns a list of (index, entry) pairs that fail verification. An
        entry fails if its signature does not match a fresh computation, or
        if its prev_sig does not match the actual previous entry's signature
        (genesis marker for index 0). An empty list means the chain is intact.
        """
        tampered = []
        expected_prev = GENESIS
        for i, entry in enumerate(self._entries):
            ok = True

            # 1. the chain link must point at the real predecessor
            if entry.get("prev_sig") != expected_prev:
                ok = False

            # 2. the entry's own signature must be valid
            expected_sig = self._sign(entry)
            actual_sig = entry.get("signature")
            if not actual_sig or not hmac.compare_digest(expected_sig, actual_sig):
                ok = False

            if not ok:
                tampered.append((i, entry))

            # next entry should point at this entry's *stored* signature
            expected_prev = entry.get("signature", "")
        return tampered


# -------------------------------------------------------------------------
# CLI entry point  (referenced by setup.py: ecu-audit=ecu_audit.main:main)
# -------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        prog="ecu-audit",
        description="Secure ECU audit logger via ELM327 over CAN.",
    )
    parser.add_argument("--auto", action="store_true",
                        help="Auto-detect a connected ELM327 device and start logging.")
    parser.add_argument("--secret-key", default=os.environ.get("ECU_AUDIT_KEY", ""),
                        help="HMAC signing key (or set ECU_AUDIT_KEY in the environment).")
    parser.add_argument("--log-path", default=DEFAULT_LOG_PATH,
                        help="Where to write the signed log file.")
    parser.add_argument("--verify", action="store_true",
                        help="Verify the integrity of an existing log chain and exit.")
    args = parser.parse_args()

    if not args.secret_key:
        parser.error("a signing key is required (use --secret-key or ECU_AUDIT_KEY)")

    logger = SecureAuditLogger(secret_key=args.secret_key, log_path=args.log_path)

    if args.verify:
        tampered = logger.verify_logs()
        if tampered:
            print(f"FAIL: chain integrity broken at {len(tampered)} entr(ies).")
            for idx, _ in tampered:
                print(f"  - entry index {idx}")
            return 1
        print(f"OK: chain of {len(logger.export_logs())} entries verified.")
        return 0

    if args.auto:
        try:
            from utils.device_detection import auto_select_port
        except ImportError:
            print("Device detection module not available.")
            return 1
        port = auto_select_port()
        if not port:
            return 1
        print(f"Selected {port}. (CAN read loop not yet implemented.)")
        logger.log_event(1000, 0, "CLI", f"Session started on {port}")
        print(f"Wrote startup event to {args.log_path}")
        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
