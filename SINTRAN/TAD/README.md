# TAD Protocol Documentation

**TAD Protocol Analysis for SINTRAN III**

---

## Overview

TAD (Terminal Access Device) protocol documentation, analyzing communication protocols used in SINTRAN III systems, particularly X.25 over HDLC encapsulation.

---

## Documents

| Document | Purpose | Description |
|----------|---------|-------------|
| [TAD-Analysis-Summary.md](TAD-Analysis-Summary.md) | Overview | Summary of TAD protocol analysis |
| [TAD-Protocol-Analysis.md](TAD-Protocol-Analysis.md) | Protocol Details | Complete protocol analysis |
| [TAD-Message-Formats.md](TAD-Message-Formats.md) | Message Structure | TAD message formats |
| [TAD-Protocol-Flows.md](TAD-Protocol-Flows.md) | Flow Diagrams | Protocol flow sequences |
| [TAD-HDLC-Encapsulation.md](TAD-HDLC-Encapsulation.md) | HDLC Layer | How TAD uses HDLC |
| [TAD-X25-CUD-Specification.md](TAD-X25-CUD-Specification.md) | X.25 Details | X.25 Call User Data |
| [TAD-Evidence-vs-Inference.md](TAD-Evidence-vs-Inference.md) | Analysis Notes | What's verified vs. inferred |

---

## Key Topics

### Protocol Layers

```
┌─────────────────────────┐
│ TAD Application Layer   │ - Terminal access
├─────────────────────────┤
│ X.25 Packet Layer      │ - Virtual circuits
├─────────────────────────┤
│ HDLC Link Layer        │ - Frame transmission
├─────────────────────────┤
│ Physical Layer         │ - Serial communication
└─────────────────────────┘
```

### HDLC Encapsulation

TAD uses HDLC for reliable frame transmission:
- Frame structure with FCS (Frame Check Sequence)
- Sequence numbers for reliability
- Flow control (RR, RNR)
- Error recovery (REJ frames)

**See:** [TAD-HDLC-Encapsulation.md](TAD-HDLC-Encapsulation.md)

### X.25 Integration

TAD implements X.25 packet layer:
- Virtual circuits
- Call setup/teardown
- Call User Data (CUD) fields
- Packet types (CALL REQUEST, CALL ACCEPTED, DATA, CLEAR)

**See:** [TAD-X25-CUD-Specification.md](TAD-X25-CUD-Specification.md)

### Message Formats

TAD-specific message structures:
- Connection requests
- Data transfers
- Acknowledgments
- Control messages

**See:** [TAD-Message-Formats.md](TAD-Message-Formats.md)

---

## Quick Start

1. **Start with:** [TAD-Analysis-Summary.md](TAD-Analysis-Summary.md) - Get overview
2. **Understand layers:** [TAD-HDLC-Encapsulation.md](TAD-HDLC-Encapsulation.md) - How HDLC is used
3. **Detailed analysis:** [TAD-Protocol-Analysis.md](TAD-Protocol-Analysis.md) - Complete protocol
4. **Message structure:** [TAD-Message-Formats.md](TAD-Message-Formats.md) - Data formats

---

## Related Documentation

### HDLC Layer
- [../Devices/HDLC/](../Devices/HDLC/) - HDLC hardware and driver
- [../Devices/HDLC/learning/03-Hardware-Overview.md](../Devices/HDLC/learning/03-Hardware-Overview.md) - COM5025 controller

### Protocol Implementation
- [../Devices/HDLC/reference/Protocol-Reference.md](../Devices/HDLC/reference/Protocol-Reference.md) - HDLC/LAPB protocols

### OS Integration
- [../OS/18-DEVICE-DRIVER-FRAMEWORK.md](../OS/18-DEVICE-DRIVER-FRAMEWORK.md) - Device drivers
- [../OS/15-DISK-IO-SUBSYSTEM.md](../OS/15-DISK-IO-SUBSYSTEM.md) - I/O subsystem

---

## Evidence-Based Analysis

TAD documentation is based on:
- ✅ Packet captures and traces
- ✅ Protocol behavior observation
- ✅ Message format analysis
- ⚠️ Some specifications inferred from behavior

**See:** [TAD-Evidence-vs-Inference.md](TAD-Evidence-vs-Inference.md) for what's verified vs. inferred.

---

## Use Cases

### For Protocol Analysis
- Understanding TAD communication
- Reverse engineering protocol
- Implementing TAD clients/servers

### For Emulation
- Emulating TAD endpoints
- Testing protocol implementations
- Debugging communication issues

### For Historical Preservation
- Documenting legacy protocols
- Understanding SINTRAN networking
- Educational purposes

---

## Version History

| Date | Version | Changes |
|------|---------|---------|
| 2025-10-17 | 1.0 | Initial TAD protocol documentation structure |

---

**Parent:** [../README.md](../README.md) - SINTRAN Documentation

