"""
ecu_audit.elm327
================

Minimal, **read-only** communication layer for ELM327-style OBD adapters,
plus a capability probe.

Scope and intent
----------------
This module exists to answer one user-facing question: *"Will this adapter
do what I expect?"* It does that by opening the serial port, sending a small
set of identity / configuration / protocol commands, and reporting what came
back.

Every command sent by this module is read-only. Nothing here writes to the
vehicle bus, changes ECU state, or issues UDS service requests. It is safe
to run against a vehicle with the ignition on.

Important caveats
-----------------
* "ELM327" is a spec with many clone implementations. A clone may *report*
  supporting something and then behave differently in practice. Treat this
  report as "what the adapter claims", not a guarantee.
* Protocol detection (ATDP/ATDPN) only returns a meaningful answer when the
  adapter is connected to a powered vehicle bus. On the bench it will
  typically report "AUTO" or an unknown protocol.
* This module talks over a serial port. A Bluetooth adapter must already be
  paired at the OS level so that it is exposed as a serial device.
"""

import time

try:
    import serial  # pyserial
except ImportError:  # pragma: no cover - dependency missing
    serial = None

# ELM327 terminates every response with the prompt character '>'.
_PROMPT = b">"

# Commands the probe sends, in order. All are read-only AT commands or
# identity queries. (command, human-readable purpose)
_PROBE_COMMANDS = [
    ("ATZ",   "Reset adapter"),
    ("ATE0",  "Disable command echo"),
    ("ATI",   "Adapter identity / firmware version"),
    ("AT@1",  "Device description"),
    ("ATDPN", "Protocol number (current)"),
    ("ATDP",  "Protocol name (current)"),
    ("ATRV",  "Read voltage at OBD connector"),
]


class ELM327Error(Exception):
    """Raised for unrecoverable communication problems (port won't open, etc.)."""


class ELM327Connection:
    """A thin, defensive wrapper around a serial connection to an ELM327.

    Use as a context manager so the port is always closed:

        with ELM327Connection(port) as conn:
            resp = conn.send_command("ATI")
    """

    def __init__(self, port, baudrate=38400, timeout=5.0):
        if serial is None:
            raise ELM327Error(
                "pyserial is not installed. Install it with: pip install pyserial"
            )
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self._ser = None

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()
        return False

    def open(self):
        try:
            self._ser = serial.Serial(
                self.port, baudrate=self.baudrate, timeout=self.timeout
            )
        except Exception as e:  # serial.SerialException and friends
            raise ELM327Error(f"Could not open serial port {self.port}: {e}")
        # Give the adapter a moment to settle after the port opens.
        time.sleep(0.5)
        try:
            self._ser.reset_input_buffer()
            self._ser.reset_output_buffer()
        except Exception:
            # Non-fatal: some virtual ports don't support buffer resets.
            pass

    def close(self):
        if self._ser is not None:
            try:
                self._ser.close()
            finally:
                self._ser = None

    def send_command(self, command):
        """Send one command and return the adapter's response as a string.

        Reads until the ELM327 prompt character ('>') or until the serial
        timeout elapses. A timeout is reported as the literal string
        "<no response>" rather than raising, so the probe can record it as a
        data point and carry on.
        """
        if self._ser is None:
            raise ELM327Error("Connection is not open.")

        try:
            self._ser.reset_input_buffer()
            self._ser.write((command + "\r").encode("ascii"))
        except Exception as e:
            raise ELM327Error(f"Failed to write '{command}' to {self.port}: {e}")

        deadline = time.time() + self.timeout
        buf = bytearray()
        while time.time() < deadline:
            try:
                chunk = self._ser.read(1)
            except Exception as e:
                raise ELM327Error(f"Failed to read response to '{command}': {e}")
            if not chunk:
                # read() returned nothing within its own timeout slice; the
                # outer deadline loop decides whether to keep waiting.
                continue
            buf += chunk
            if chunk == _PROMPT:
                break

        if not buf:
            return "<no response>"

        # Clean up: drop the prompt, normalise line endings, strip the echoed
        # command if echo was still on, and collapse blank lines.
        text = buf.replace(_PROMPT, b"").decode("ascii", errors="replace")
        lines = [ln.strip() for ln in text.replace("\r", "\n").split("\n")]
        lines = [ln for ln in lines if ln and ln != command]
        return " ".join(lines) if lines else "<no response>"


# --------------------------------------------------------------------------
# Capability probe
# --------------------------------------------------------------------------

def probe_capabilities(port, timeout=5.0):
    """Run the read-only probe sequence against an adapter.

    Returns a dict describing the outcome. The shape is stable so the web
    layer can render it without guessing:

        {
          "port": "/dev/cu.OBDII",
          "connected": True/False,
          "error": None or "human readable reason",
          "results": [
              {"command": "ATI", "purpose": "...",
               "response": "...", "responded": True/False},
              ...
          ],
          "summary": {
              "identity":   "..." or None,
              "description":"..." or None,
              "protocol_number": "..." or None,
              "protocol_name":   "..." or None,
              "voltage":         "..." or None,
              "responsive": True/False,   # did the adapter answer anything?
          },
        }

    This function never raises for communication problems -- it captures
    them in the "error" / "connected" fields so the caller always gets a
    structured result to display.
    """
    result = {
        "port": port,
        "connected": False,
        "error": None,
        "results": [],
        "summary": {
            "identity": None,
            "description": None,
            "protocol_number": None,
            "protocol_name": None,
            "voltage": None,
            "responsive": False,
        },
    }

    try:
        conn = ELM327Connection(port, timeout=timeout)
        conn.open()
    except ELM327Error as e:
        result["error"] = str(e)
        return result

    result["connected"] = True
    try:
        for command, purpose in _PROBE_COMMANDS:
            try:
                response = conn.send_command(command)
            except ELM327Error as e:
                response = f"<error: {e}>"
            responded = not (
                response == "<no response>" or response.startswith("<error")
            )
            result["results"].append({
                "command": command,
                "purpose": purpose,
                "response": response,
                "responded": responded,
            })
    finally:
        conn.close()

    # Fold the raw results into a friendlier summary.
    by_cmd = {r["command"]: r for r in result["results"]}

    def _val(cmd):
        r = by_cmd.get(cmd)
        return r["response"] if r and r["responded"] else None

    result["summary"]["identity"] = _val("ATI")
    result["summary"]["description"] = _val("AT@1")
    result["summary"]["protocol_number"] = _val("ATDPN")
    result["summary"]["protocol_name"] = _val("ATDP")
    result["summary"]["voltage"] = _val("ATRV")
    result["summary"]["responsive"] = any(
        r["responded"] for r in result["results"]
    )

    return result
