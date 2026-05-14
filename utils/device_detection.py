
"""Serial-port detection for ELM327 / OBD adapters.

Detection is best-effort: adapter naming is wildly inconsistent across
vendors, OSes, and connection types (USB vs Bluetooth). USB adapters usually
carry "ELM327", "OBD", or a USB-serial chipset name in their description.
Bluetooth adapters, once paired at the OS level, often appear under a name
like "OBDII", "OBD-II", or the vendor's device name -- which is why the
match list below also looks at the port's device path, not just its
description.

If your adapter is connected (and, for Bluetooth, paired) but not detected,
it is almost certainly a naming gap rather than a hardware fault -- the port
can still be probed directly by passing its path explicitly.
"""

from serial.tools import list_ports
import serial  # noqa: F401  (kept for callers that import serial via this module)

# Case-insensitive substrings that suggest a port is an ELM327 / OBD adapter.
# Checked against both the port description and the device path.
_MATCH_HINTS = (
    "elm327",
    "obd",
    "usb-serial",
    "usbserial",   # common macOS USB-serial naming
    "ftdi",        # frequent ELM327 USB chipset
    "ch340",       # frequent ELM327 USB chipset
    "ch341",
)


def _looks_like_adapter(port):
    """True if a pyserial ListPortInfo looks like an OBD adapter."""
    haystack = " ".join(
        str(x).lower() for x in (port.description, port.device, port.name)
        if x
    )
    return any(hint in haystack for hint in _MATCH_HINTS)


def detect_elm327_ports():
    """Return a list of (device_path, description) for likely adapters."""
    elm_ports = []
    for port in list_ports.comports():
        if _looks_like_adapter(port):
            elm_ports.append((port.device, port.description))
    return elm_ports


def list_all_ports():
    """Return every serial port as (device_path, description).

    Useful as a fallback when detection finds nothing but the user knows an
    adapter is connected -- they can pick the right port manually.
    """
    return [(p.device, p.description) for p in list_ports.comports()]


def auto_select_port():
    """Interactive CLI helper: pick an adapter port, prompting if ambiguous."""
    ports = detect_elm327_ports()
    if not ports:
        print("No ELM327-like devices found.")
        return None
    if len(ports) == 1:
        print(f"Found ELM327 device: {ports[0][1]} ({ports[0][0]})")
        return ports[0][0]
    print("Multiple devices found:")
    for i, (port, desc) in enumerate(ports):
        print(f"  {i + 1}. {desc} ({port})")
    try:
        idx = int(input(f"Select device to use [1-{len(ports)}]: ")) - 1
    except (ValueError, EOFError):
        print("Invalid selection.")
        return None
    if not 0 <= idx < len(ports):
        print("Selection out of range.")
        return None
    return ports[idx][0]
