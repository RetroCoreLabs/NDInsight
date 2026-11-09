# Editor Documentation

This folder contains comprehensive documentation for the SINTRAN text editors.

---

## 📝 Available Editors

SINTRAN III provides three powerful text editors, each suited for different use cases:

| Editor | Name | Best For | Guide |
|--------|------|----------|-------|
| **QED** | Quick Editor | Interactive editing, quick fixes | [QED-QUICK-REFERENCE.md](QED-QUICK-REFERENCE.md) |
| **PED** | Program Editor | Program development, structured editing | [PED-QUICK-REFERENCE.md](PED-QUICK-REFERENCE.md) |
| **LED** | Line Editor | Batch editing, scripts | *See EDITORS-GUIDE.md* |

---

## 📖 Documentation Files

### [EDITORS-GUIDE.md](EDITORS-GUIDE.md)
**Complete editor overview and feature comparison**
- All three editors (QED, PED, LED)
- Feature comparison matrix
- Command syntax and patterns
- Best practices and workflow tips

### [QED-QUICK-REFERENCE.md](QED-QUICK-REFERENCE.md)
**QED Quick Reference Card**
- Command summary
- Common patterns
- Navigation shortcuts
- Search and replace

### [PED-QUICK-REFERENCE.md](PED-QUICK-REFERENCE.md)
**PED Quick Reference Card**
- Command summary
- Program development features
- Line numbering and organization
- File operations

---

## 🎯 Which Editor to Use?

### Use QED When:
- Making quick edits to existing files
- Working interactively at the terminal
- Need fast, responsive editing
- Editing small to medium files

### Use PED When:
- Developing programs
- Need structured line numbering
- Working with larger source files
- Want advanced program-specific features

### Use LED When:
- Running batch edit operations
- Scripting automated edits
- Processing multiple files
- Non-interactive editing

---

## 📚 Reference Manuals

For complete reference documentation, see:
- **QED**: [ND-60.031.04 EN QED User Manual](../../Reference-Manuals/ND-60.031.04%20EN%20QED%20User%20Manual.md)
- **PED**: [ND-60.121.4 PED User's Guide](../../Reference-Manuals/ND-60.121.4%20PED%20User's%20Guide.md)

---

## 🚀 Quick Start Examples

### Starting an Editor
```
@QED filename           - Edit with QED
@PED filename           - Edit with PED
@LED filename < script  - Batch edit with LED
```

### Common QED Commands
```
1,10p     - Print lines 1-10
/text/    - Search for "text"
s/old/new/g - Replace old with new globally
w         - Write changes
q         - Quit
```

### Common PED Commands
```
L         - List file
10        - Go to line 10
I text    - Insert text at current position
D5        - Delete 5 lines
S         - Save
E         - Exit
```

---

## 🔗 Related Documentation

- **Main Developer Guide**: [../README.md](../README.md)
- **Language Guides**: [../Languages/](../Languages/)
- **Workflow Guides**: [../Workflow/](../Workflow/)
- **SINTRAN Commands**: [../../Reference-Manuals/SINTRAN-COMMANDS-REFERENCE.md](../../Reference-Manuals/SINTRAN-COMMANDS-REFERENCE.md)

---

**Last Updated**: October 18, 2025  
**Documentation Status**: ✅ Complete

