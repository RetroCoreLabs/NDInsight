# SINTRAN HDLC Implementation Documentation

**Complete documentation for understanding and implementing the SINTRAN III HDLC (High-Level Data Link Control) subsystem.**

---

## 🎯 Quick Start - Choose Your Path

### 👋 I'm New to SINTRAN HDLC
**Start here if**: You want to understand the basics before diving into details.

📚 **Your Path**:
1. [Getting Started](learning/01-Getting-Started.md) - System overview and architecture
2. [Understanding Packets](learning/02-Understanding-Packets.md) - How HDLC packets work
3. [Hardware Overview](learning/03-Hardware-Overview.md) - COM5025, X.21, DMA
4. [Software Flow](learning/04-Software-Flow.md) - SINTRAN HDLC software structure

### 🎮 I Need to Build an Emulator
**Start here if**: You're implementing a SINTRAN HDLC emulator in C# or another language.

🔧 **Your Path**:
1. [Getting Started](learning/01-Getting-Started.md) - Quick orientation
2. [Register Reference](reference/Register-Reference.md) - Complete register specs
3. [DMA Reference](reference/DMA-Reference.md) - DMA descriptor details
4. [Emulator Implementation Guide](implementation/Emulator-Implementation-Guide.md) - Build it step-by-step
5. [Testing Scenarios](implementation/Testing-Scenarios.md) - Test your implementation
6. [Debugging Guide](implementation/Debugging-Guide.md) - Troubleshoot issues

### 🛠️ I'm Writing a Program That Uses HDLC
**Start here if**: You want to send/receive HDLC frames from your own SINTRAN program (and run it under nd100x).

⚙️ **Your Path**:
1. [HDLC Raw Programming Guide](HDLC-Raw-Programming-Guide.md) - MON 201B API, DCB layout, send/receive flow
2. [Buffer-Pool and Emulator Usage](implementation/Buffer-Pool-and-Emulator-Usage.md) - `CHANGE-BUFFER-SIZE` setup, pool sizing, the receive-arm trap, running under nd100x
3. [MAC Cookbook](../../../Developer/Languages/System/MAC-COOKBOOK.md) - writing the MAC program itself (source encoding, monitor-call ABI, file I/O)

### 🔍 I'm Debugging an Existing System
**Start here if**: Something isn't working and you need to figure out why.

⚡ **Your Path**:
1. [Quick Reference Card](Quick-Reference-Card.md) - Critical constants and patterns
2. [Debugging Guide](implementation/Debugging-Guide.md) - Troubleshooting strategies
3. [Register Reference](reference/Register-Reference.md) - Verify bit definitions
4. [Interrupt Reference](reference/Interrupt-Reference.md) - Check interrupt logic
5. [HDLC-ALL.md](HDLC-ALL.md) - Search for specific topics

### 🔬 I Need Deep Technical Understanding
**Start here if**: You want to understand every detail and breakthrough discovery.

📖 **Your Path**:
1. Read all [Learning Documents](learning/) - Build foundation
2. Read all [Reference Documents](reference/) - Complete specifications
3. Read all [Deep Dives](deep-dives/) - Advanced discoveries
4. Read [Complete Pseudocode](appendices/Appendix-A-Pseudocode.md) - Source code level
5. Explore [HDLC-ALL.md](HDLC-ALL.md) - Everything in one place

---

## 📚 Documentation Structure

### Learning Track (Start Here for Newcomers)
**Progressive introduction to SINTRAN HDLC**

| Document | Description | Lines |
|----------|-------------|-------|
| [01-Getting-Started.md](learning/01-Getting-Started.md) | System architecture and component overview | ~300 |
| [02-Understanding-Packets.md](learning/02-Understanding-Packets.md) | HDLC packet structure and lifecycle | ~250 |
| [03-Hardware-Overview.md](learning/03-Hardware-Overview.md) | COM5025, X.21 interface, IOX bus | ~400 |
| [04-Software-Flow.md](learning/04-Software-Flow.md) | SINTRAN software organization | ~350 |

### Technical Reference (Complete Specifications)
**Detailed technical reference material**

| Document | Description | Lines |
|----------|-------------|-------|
| [Register-Reference.md](reference/Register-Reference.md) | Complete register map and bit definitions | ~600 |
| [DMA-Reference.md](reference/DMA-Reference.md) | DMA descriptors, LKEY field, operations | ~500 |
| [Interrupt-Reference.md](reference/Interrupt-Reference.md) | HIINT/HOINT analysis, WRTC/WTTC control | ~700 |
| [Protocol-Reference.md](reference/Protocol-Reference.md) | LAPB, X.25, X.21, PAD protocols | ~500 |

### Implementation Guides (Practical)
**Step-by-step implementation guidance**

| Document | Description | Lines |
|----------|-------------|-------|
| [Emulator-Implementation-Guide.md](implementation/Emulator-Implementation-Guide.md) | Complete emulator development guide | ~800 |
| [Buffer-Pool-and-Emulator-Usage.md](implementation/Buffer-Pool-and-Emulator-Usage.md) | Buffer setup (`CHANGE-BUFFER-SIZE`), pool sizing, receive-arm tuning, running HDLC apps under nd100x | ~230 |
| [Testing-Scenarios.md](implementation/Testing-Scenarios.md) | Comprehensive test cases | ~400 |
| [Debugging-Guide.md](implementation/Debugging-Guide.md) | Troubleshooting and debugging strategies | ~450 |

### Deep Dives (Advanced Topics)
**In-depth analysis of breakthrough discoveries**

| Document | Description | Lines |
|----------|-------------|-------|
| [Deep-Dive-COM5025-Interface.md](deep-dives/Deep-Dive-COM5025-Interface.md) | LKEY field breakthrough discovery | ~400 |
| [Deep-Dive-Interrupt-Control.md](deep-dives/Deep-Dive-Interrupt-Control.md) | WRTC/WTTC interrupt enable analysis | ~400 |
| [Deep-Dive-XSSDATA.md](deep-dives/Deep-Dive-XSSDATA.md) | Complete transmitter analysis | ~500 |
| [Deep-Dive-PROCPKT.md](deep-dives/Deep-Dive-PROCPKT.md) | Complete receiver packet processing | ~500 |

### Appendices (Reference Data)
**Complete pseudocode, constants, traces, history**

| Document | Description | Lines |
|----------|-------------|-------|
| [Appendix-A-Pseudocode.md](appendices/Appendix-A-Pseudocode.md) | Complete SINTRAN HDLC pseudocode | ~1000 |
| [Appendix-B-Constants-Variables.md](appendices/Appendix-B-Constants-Variables.md) | All constants, variables, memory map | ~600 |
| [Appendix-C-Packet-Traces.md](appendices/Appendix-C-Packet-Traces.md) | Real packet trace analysis | ~800 |
| [Appendix-D-Bug-History.md](appendices/Appendix-D-Bug-History.md) | Bug discoveries and corrections | ~400 |

### Special Documents
**Comprehensive reference and quick lookup**

| Document | Description | Size |
|----------|-------------|------|
| [HDLC-ALL.md](HDLC-ALL.md) | **Master reference** - All content aggregated for searching | 23,358 lines |
| [Quick-Reference-Card.md](Quick-Reference-Card.md) | One-page cheat sheet with critical info | ~150 lines |
| [01-HDLC-Hardware-Reference.md](01-HDLC-Hardware-Reference.md) | Consolidated hardware reference (root copy) | - |
| [REORGANIZATION-PROPOSAL.md](REORGANIZATION-PROPOSAL.md) | Documentation reorganization proposal | - |
| [REORGANIZATION-SUMMARY.md](REORGANIZATION-SUMMARY.md) | Summary of documentation reorganization | - |

---

## 🔑 Key Concepts at a Glance

### What is SINTRAN HDLC?
SINTRAN III's implementation of the HDLC protocol for synchronous serial communication over X.21 interfaces. It provides reliable, frame-based data transmission for terminal connections and network communications.

### Core Components
- **COM5025 Chip**: Multi-protocol communications controller handling HDLC framing
- **X.21 Interface**: Physical layer for synchronous serial communication
- **DMA Controller**: Hardware-based buffer management for efficient data transfer
- **SINTRAN Software**: Interrupt handlers, buffer management, protocol implementation

### Critical Discoveries
1. **LKEY Field Structure**: DMA descriptor bits 7-0 contain actual COM5025 register values
2. **WRTC/WTTC Control**: Specific values (1734₈, 1134₈) enable comprehensive interrupt generation
3. **Success Test**: Transmission success = `(RTTS & 0x8002) == 0` (SILFO+TXUND both clear)
4. **ACTSW Gate**: Activity switch controls all interrupt processing

---

## 📖 Key Terminology

| Term | Description |
|------|-------------|
| **HDLC** | High-Level Data Link Control - bit-oriented protocol |
| **LAPB** | Link Access Procedure Balanced - HDLC implementation for X.25 |
| **X.25** | Packet switching protocol built on LAPB |
| **X.21** | Physical interface standard for synchronous serial communication |
| **COM5025** | SMC/AMD multi-protocol communications controller chip |
| **DMA** | Direct Memory Access - hardware-based data transfer |
| **LKEY** | DMA descriptor control word containing block status and COM5025 bits |
| **RRTS** | Read Receiver Transfer Status - primary receiver status register |
| **RTTS** | Read Transmitter Transfer Status - primary transmitter status register |
| **WRTC** | Write Receiver Transfer Control - receiver interrupt enable |
| **WTTC** | Write Transmitter Transfer Control - transmitter interrupt enable |
| **HIINT** | Receiver interrupt handler (Hardware Input INTerrupt) |
| **HOINT** | Transmitter interrupt handler (Hardware Output INTerrupt) |
| **ACTSW** | Activity Switch - master control for device active state |
| **HASTAT** | Hardware STATus - variable storing RRTS/RTTS values |
| **FSERM** | Frame Start/End Marker - DMA key for single-block frames (002003₈) |
| **SILFO** | Serial Illegal FOrmat - transmitter error bit (bit 15) |
| **TXUND** | Transmitter UNDeRrun - transmitter error bit (bit 1) |
| **IOX** | Input/Output eXtension - register addressing system |

---

## 🎓 Learning Resources

### For Visual Learners
All documents include Mermaid diagrams following [MERMAID_COLOR_STANDARDS.md](../MERMAID_COLOR_STANDARDS.md):
- System architecture diagrams
- Data flow charts
- State machines
- Protocol stack visualizations

### For Code-Focused Developers
Complete pseudocode and C# implementation examples throughout:
- [Appendix A: Complete Pseudocode](appendices/Appendix-A-Pseudocode.md)
- [Emulator Implementation Guide](implementation/Emulator-Implementation-Guide.md)
- Code snippets in all technical documents

### For Hardware Engineers
Detailed hardware specifications:
- [Hardware Overview](learning/03-Hardware-Overview.md)
- [Register Reference](reference/Register-Reference.md)
- [Deep Dive: COM5025 Interface](deep-dives/Deep-Dive-COM5025-Interface.md)

---

## 🚀 Quick Navigation by Topic

### By Component
- **COM5025 Chip**: [Hardware Overview](learning/03-Hardware-Overview.md) → [Deep Dive: COM5025](deep-dives/Deep-Dive-COM5025-Interface.md)
- **X.21 Interface**: [Hardware Overview](learning/03-Hardware-Overview.md) → [Protocol Reference](reference/Protocol-Reference.md)
- **DMA System**: [DMA Reference](reference/DMA-Reference.md) → [Software Flow](learning/04-Software-Flow.md)
- **Registers**: [Register Reference](reference/Register-Reference.md) → [Quick Reference Card](Quick-Reference-Card.md)

### By Task
- **Understanding Packets**: [Understanding Packets](learning/02-Understanding-Packets.md) → [Protocol Reference](reference/Protocol-Reference.md)
- **Implementing Transmitter**: [Software Flow](learning/04-Software-Flow.md) → [Deep Dive: XSSDATA](deep-dives/Deep-Dive-XSSDATA.md)
- **Implementing Receiver**: [Software Flow](learning/04-Software-Flow.md) → [Deep Dive: PROCPKT](deep-dives/Deep-Dive-PROCPKT.md)
- **Handling Interrupts**: [Interrupt Reference](reference/Interrupt-Reference.md) → [Deep Dive: Interrupt Control](deep-dives/Deep-Dive-Interrupt-Control.md)

### By Problem
- **Packets Not Sending**: [Debugging Guide](implementation/Debugging-Guide.md) → [Register Reference](reference/Register-Reference.md)
- **Packets Not Receiving**: [Debugging Guide](implementation/Debugging-Guide.md) → [Interrupt Reference](reference/Interrupt-Reference.md)
- **Retransmission Issues**: [Deep Dive: XSSDATA](deep-dives/Deep-Dive-XSSDATA.md) → [Appendix A: Pseudocode](appendices/Appendix-A-Pseudocode.md)
- **Status Bit Confusion**: [Quick Reference Card](Quick-Reference-Card.md) → [Register Reference](reference/Register-Reference.md)

---

## 📊 Document Statistics

- **Total Documentation**: 20 focused documents + HDLC-ALL master reference
- **Learning Documents**: 4 files (~1,300 lines)
- **Reference Documents**: 4 files (~2,300 lines)
- **Implementation Guides**: 3 files (~1,650 lines)
- **Deep Dives**: 4 files (~1,800 lines)
- **Appendices**: 4 files (~2,800 lines)
- **Master Reference**: HDLC-ALL.md (23,358 lines, 0.84 MB)

---

## 🔄 Document Updates

This documentation was reorganized from comprehensive analysis files to provide:
- ✅ Clear entry points for different audiences
- ✅ Progressive disclosure (simple → complex)
- ✅ Practical implementation guidance
- ✅ Complete technical reference
- ✅ Preserved historical analysis

**Last Major Reorganization**: Current session  
**Source Material**: 59 analysis files consolidated into structured documentation

---

## 🤝 Contributing & Maintenance

### Updating Documentation
When updating this documentation:
1. Maintain consistency across related documents
2. Update cross-references when moving content
3. Follow Mermaid color standards for diagrams
4. Keep HDLC-ALL.md synchronized with detailed docs
5. Update this README when adding new documents

### Document Standards
- Clear purpose statement at document start
- Table of contents for documents >200 lines
- "See Also" sections for related documents
- Code examples with proper syntax highlighting
- Mermaid diagrams following project standards

---

## 📞 Need Help?

### Start Here
1. **Not sure where to begin?** → Read [Getting Started](learning/01-Getting-Started.md)
2. **Looking for something specific?** → Search [HDLC-ALL.md](HDLC-ALL.md)
3. **Need quick lookup?** → Check [Quick Reference Card](Quick-Reference-Card.md)
4. **Having problems?** → Read [Debugging Guide](implementation/Debugging-Guide.md)

### Document Map
```
📁 hdlc-analysis/
├── 📖 README.md ← You are here
├── ⚡ Quick-Reference-Card.md
├── 📚 learning/ (4 docs - start here if new)
├── 📋 reference/ (4 docs - technical specs)
├── 🎮 implementation/ (3 docs - build & debug)
├── 🔬 deep-dives/ (4 docs - advanced topics)
├── 📝 appendices/ (4 docs - reference data)
└── 📚 HDLC-ALL.md (master reference - 23K lines)
```

---

**Ready to start? Pick your path above and dive in!** 🚀
