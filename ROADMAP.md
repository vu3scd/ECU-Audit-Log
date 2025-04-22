
# 🛡️ ECU Audit CLI + Web Viewer – Regulatory-Aligned Roadmap

_A project by Sumit Chouhan designed to support cybersecurity logging and diagnostics across modern ECUs using ELM327 over CAN._

---

## v0.1 – MVP (Completed)
- CLI logging from ECUs via ELM327 + CAN
- HMAC-signed local log storage
- Searchable dashboard using Flask
- Docker support, GitHub Actions, GitHub Pages
- MIT License and v0.1.0 release

---

## v0.2 – Compliance Hardening  
ISO/SAE 21434 Clause 11, UN R155 Annex 5  
- [ ] Log critical security events per UN R155 Annex 5 (e.g., login failures, memory access errors)
- [ ] Implement log retention policy aligned with Clause 11.4
- [ ] Log export formats: encrypted JSON/CSV
- [ ] Start event severity tagging for Clause 11.2 monitoring granularity

---

## v0.3 – Secure Diagnostics & UDS  
ISO 21434 Clause 15, UN R156  
- [ ] Implement UDS log requests (e.g., 0x19, 0x22)
- [ ] Log software update attempts (UN R156 §6.1)
- [ ] Add support for diagnostic session logs and change tracking
- [ ] Export logs in structured, readable formats for audit & testing teams

---

## v0.4 – Gateway Mode & Cloud Forwarding  
UN R155 (CSMS), ISO 21177  
- [ ] Support multi-ECU systems (e.g., 0x7E8, 0x7EA)
- [ ] Create gateway log collector that aggregates logs from multiple ECUs
- [ ] Add MQTT or HTTPS transport to export logs to backend/cloud
- [ ] Support integration with ISO 21177/21185 formats

---

## v1.0 – Production Grade  
Full ISO/SAE 21434 Organizational + Validation Readiness  
- [ ] Link logs to TARA-derived threats (Annex E)
- [ ] Chain-of-custody support: log verification and integrity reports
- [ ] Add web UI access control (basic auth or OAuth)
- [ ] Create ISO/UNR mapping table: What’s logged vs what’s required
- [ ] Full GitHub Pages documentation + threat logging guidance

---

## Long-Term Enhancements
- [ ] Real-time CAN fuzz detection (simple IDS)
- [ ] Integration with Raspberry Pi + CAN HAT for demo rigs
- [ ] Developer API for custom ECU apps to push logs
- [ ] OpenTelemetry support for vehicle-wide observability

---

_This roadmap evolves as the project matures and compliance frameworks evolve._
