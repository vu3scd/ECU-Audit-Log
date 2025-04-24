
## 🔄 v0.2.0 Updates

- ✅ Auto-detects ELM327 or compatible USB/Bluetooth devices
- ✅ CLI now probes connected serial ports and prompts for selection
- ✅ Improves usability across Windows, Linux, macOS

## Usage (Updated)
```bash
ecu-audit --auto
```
You will be prompted to select from detected ports (e.g. COM5, /dev/ttyUSB0)

To still specify a port manually:
```bash
ecu-audit --channel COM3 --dump logs.json
```
