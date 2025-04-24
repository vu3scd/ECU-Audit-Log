
from serial.tools import list_ports
import serial

def detect_elm327_ports():
    ports = list_ports.comports()
    elm_ports = []
    for port in ports:
        if "ELM327" in port.description or "OBD" in port.description or "USB-SERIAL" in port.description:
            elm_ports.append((port.device, port.description))
    return elm_ports

def auto_select_port():
    ports = detect_elm327_ports()
    if not ports:
        print("❌ No ELM327-like devices found.")
        return None
    if len(ports) == 1:
        print(f"✅ Found ELM327 device: {ports[0][1]}")
        return ports[0][0]
    print("🔍 Multiple devices found:")
    for i, (port, desc) in enumerate(ports):
        print(f"  {i + 1}. {desc} ({port})")
    idx = int(input("Select device to use [1-{0}]: ".format(len(ports)))) - 1
    return ports[idx][0]
