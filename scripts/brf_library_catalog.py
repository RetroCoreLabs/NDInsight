#!/usr/bin/env python3
"""Make the link-library catalog: every entry point in every :BRF library on the archive floppies.

It reads every floppy image in the Norsk Data Software Archive, takes out every :BRF file,
parses each one with nd100_brf.py (every unit's checksum is checked) and writes two documents:

  LINK-LIBRARY-ENTRY-POINTS.md   per library file: where it was found, how many units, and
                                 every name it defines (MAIN and ENTR symbols)
  LINK-LIBRARY-NAME-INDEX.md     per name: which libraries define it

Identical copies of a file (same bytes) are listed once. Two files with the same name but
different bytes are listed separately and marked.

Use:
  python brf_library_catalog.py --archive <archive-checkout> --out <folder for the two .md files>

The ndfs reader must be importable: install it, or point NDFS_PY_SRC at its "src" folder
(the norskdata-ndfs repository, ndfs-py/src).
"""
from __future__ import annotations

import argparse
import glob
import gzip
import hashlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
if os.environ.get("NDFS_PY_SRC"):
    sys.path.insert(0, os.environ["NDFS_PY_SRC"])

import nd100_brf  # noqa: E402
from ndfs import NdfsFileSystem  # noqa: E402

# File-name prefix -> language or product family. First match wins.
FAMILIES = [
    ("FORT", "FORTRAN"), ("F32FORT", "FORTRAN"), ("FTN", "FORTRAN"), ("FORTRAN", "FORTRAN"),
    ("PLANC", "PLANC"), ("PLC", "PLANC"),
    ("MON-CALL", "Monitor calls"), ("MONCALL", "Monitor calls"),
    ("PASCAL", "Pascal"), ("PAS", "Pascal"), ("EXTRA-PAS", "Pascal"),
    ("COBOL", "COBOL"), ("COBLIB", "COBOL"), ("CB-", "COBOL"),
    ("BAS", "BASIC"), ("CC-", "C"), ("HPLIB", "Hardware / HP library"),
    ("SCREEN", "Screen handling"), ("VTM", "Screen handling"), ("MLE", "Screen handling"),
    ("ISAM", "ISAM"), ("XMP", "COSMOS / XMSG"), ("TLX", "Telex"), ("UNIQ", "Unique"),
    ("JEC", "JEC"), ("SIBAS", "SIBAS"), ("NOTIS", "NOTIS"),
]


def family(name: str) -> str:
    for prefix, fam in FAMILIES:
        if name.startswith(prefix):
            return fam
    return "Other"


def scan(archive: str):
    root = os.path.join(archive, "images")
    images = sorted(glob.glob(root + "/*/*.img.gz") + glob.glob(root + "/*/*.img"))
    found = {}   # md5 of the BRF bytes -> record
    stats = {"images": len(images), "opened": 0, "not_ndfs": 0, "brf_files": 0}
    for path in images:
        try:
            raw = gzip.open(path, "rb").read() if path.endswith(".gz") else open(path, "rb").read()
            fs = NdfsFileSystem(raw, read_only=True)
            entries = fs.get_object_entries()
        except Exception:
            stats["not_ndfs"] += 1
            continue
        stats["opened"] += 1
        volume = fs.get_directory_name()
        image_id = os.path.basename(os.path.dirname(path))[:8]
        for o in entries:
            if o.type != "BRF":
                continue
            data = fs.read_file("%s/%s:%s" % (o.user_name, o.object_name, o.type), parity="none")
            stats["brf_files"] += 1
            md5 = hashlib.md5(data).hexdigest()
            where = "%s [%s]" % (volume, image_id)
            if md5 in found:
                found[md5]["where"].append(where)
                continue
            parsed = nd100_brf.parse_brf(data)
            units = parsed.units
            defs = sorted({s.name for u in units for s in u.symbols if s.kind in ("MAIN", "ENTR")})
            found[md5] = {
                "name": o.object_name, "bytes": len(data), "where": [where], "md5": md5,
                "units": len(units),
                "lib_units": sum(1 for u in units if any(s.kind == "LIBR" for s in u.symbols)),
                "bad": sum(1 for u in units if u.checksum_ok is not True),
                # identification text: only from a unit whose checksum is right, short, and plain text
                "ident": next((u.comment for u in units
                               if u.comment and u.checksum_ok and len(u.comment) <= 60
                               and all(32 <= ord(ch) < 127 for ch in u.comment)), ""),
                "defs": defs,
            }
    return found, stats


def wrap_names(names, width=100):
    lines, cur = [], ""
    for n in names:
        piece = n + " "
        if len(cur) + len(piece) > width:
            lines.append(cur.rstrip())
            cur = ""
        cur += piece
    if cur:
        lines.append(cur.rstrip())
    return lines


def label(rec, same_name_count, index):
    suffix = "" if same_name_count == 1 else "  (version %d of %d with this name)" % (index, same_name_count)
    return rec["name"] + suffix


def write_entry_doc(path, found, stats):
    recs = sorted(found.values(), key=lambda r: (family(r["name"]), r["name"], r["md5"]))
    by_name = {}
    for r in recs:
        by_name.setdefault(r["name"], []).append(r)
    libs = [r for r in recs if r["lib_units"]]
    objs = [r for r in recs if not r["lib_units"]]
    total_names = sum(len(r["defs"]) for r in libs)
    out = []
    out.append("# Link Libraries: Entry Points\n")
    out.append("Generated by `scripts/brf_library_catalog.py`. Do not edit by hand.\n")
    out.append("Every `:BRF` file on the Norsk Data Software Archive floppies, with every name it defines.\n"
               "This is what `LOAD` in the BRF linker can resolve. To see which libraries define a name, see "
               "[LINK-LIBRARY-NAME-INDEX.md](LINK-LIBRARY-NAME-INDEX.md).\n")
    out.append("**How it was made.** %d floppy images were read; %d are NDFS volumes (the others are not). "
               "%d `:BRF` files were found, %d with different contents. Each was parsed by "
               "[nd100_brf.py](../../scripts/nd100_brf.py), which checks every unit's checksum. "
               "The parser was compared with the BRF linker's own `LIST-BRF-ENTRIES` on "
               "`FORT48-2BANK-F02:BRF`: 462 of 462 names identical.\n"
               % (stats["images"], stats["opened"], stats["brf_files"], len(recs)))
    out.append("**Library or not.** A *library file* has units that start with a LIBR group: the linker loads such "
               "a unit only when something refers to one of its names. %d of the files are libraries "
               "(%d names in them). The other %d are ordinary object files and are listed at the end by name only.\n"
               % (len(libs), total_names, len(objs)))
    out.append("**Checksum column.** `ok` means every unit's checksum is correct. `N of M units fail` means the file is "
               "damaged, or holds a group this parser reads wrongly. A copy with failures often sits next to a good "
               "copy of the same file (compare the sizes and the volumes).\n")
    out.append("**Using it.** The six-bit symbol names are at most 7 characters. When the linker says "
               "`Undefined entries`, look the name up in the index, then `LOAD` the library that defines it.\n")

    out.append("## Index of libraries\n")
    out.append("| Family | Library file | Found on (volume [archive id]) | Units | Names | Checksums | Identification text |")
    out.append("|---|---|---|---:|---:|---|---|")
    for r in libs:
        n_same = len(by_name[r["name"]])
        idx = by_name[r["name"]].index(r) + 1
        where = "; ".join(sorted(set(r["where"]))[:2]) + (" +%d" % (len(set(r["where"])) - 2) if len(set(r["where"])) > 2 else "")
        ok = "ok" if not r["bad"] else "%d of %d units fail" % (r["bad"], r["units"])
        out.append("| %s | `%s` | %s | %d | %d | %s | %s |" % (
            family(r["name"]), label(r, n_same, idx), where, r["units"], len(r["defs"]), ok, r["ident"]))
    out.append("")

    out.append("## Entry points per library\n")
    last_family = None
    for r in libs:
        fam = family(r["name"])
        if fam != last_family:
            out.append("### %s\n" % fam)
            last_family = fam
        n_same = len(by_name[r["name"]])
        idx = by_name[r["name"]].index(r) + 1
        out.append("#### `%s`\n" % label(r, n_same, idx))
        out.append("%d units (%d library units), %d bytes, %d names. MD5 `%s`. Checksums: %s.%s\n" % (
            r["units"], r["lib_units"], r["bytes"], len(r["defs"]), r["md5"],
            "ok" if not r["bad"] else "%d of %d units fail" % (r["bad"], r["units"]),
            ("  Identification: " + r["ident"] + ".") if r["ident"] else ""))
        out.append("Found on: " + "; ".join(sorted(set(r["where"]))) + "\n")
        out.append("```")
        out.extend(wrap_names(r["defs"]))
        out.append("```\n")

    out.append("## Ordinary object files (not libraries)\n")
    out.append("These have no LIBR units: the linker always loads them. Names only.\n")
    out.append("| File | Found on | Units | Names | Checksums |")
    out.append("|---|---|---:|---:|---|")
    for r in sorted(objs, key=lambda r: (r["name"], r["md5"])):
        n_same = len(by_name[r["name"]])
        idx = by_name[r["name"]].index(r) + 1
        where = "; ".join(sorted(set(r["where"]))[:2]) + (" +%d" % (len(set(r["where"])) - 2) if len(set(r["where"])) > 2 else "")
        ok = "ok" if not r["bad"] else "%d of %d units fail" % (r["bad"], r["units"])
        out.append("| `%s` | %s | %d | %d | %s |" % (label(r, n_same, idx), where, r["units"], len(r["defs"]), ok))
    out.append("")
    open(path, "w", encoding="utf-8", newline="\n").write("\n".join(out))


def write_index_doc(path, found, lookfor):
    recs = [r for r in found.values() if r["lib_units"]]
    by_name = {}
    for r in recs:
        by_name.setdefault(r["name"], []).append(r)
    where = {}   # entry name -> sorted set of library labels
    for r in recs:
        n_same = len(by_name[r["name"]])
        idx = by_name[r["name"]].index(r) + 1
        for d in r["defs"]:
            where.setdefault(d, set()).add(label(r, n_same, idx).split("  (")[0])
    out = []
    out.append("# Link Libraries: Name Index\n")
    out.append("Generated by `scripts/brf_library_catalog.py`. Do not edit by hand.\n")
    out.append("Which library defines a name? One line per name, libraries separated by commas. "
               "Libraries here are the `:BRF` files with LIBR units; see "
               "[LINK-LIBRARY-ENTRY-POINTS.md](LINK-LIBRARY-ENTRY-POINTS.md) for the files themselves. "
               "%d distinct names.\n" % len(where))
    out.append("## Names people look for\n")
    out.append("| Name | Defined by |")
    out.append("|---|---|")
    for n in lookfor:
        libs = sorted(where.get(n, []))
        out.append("| `%s` | %s |" % (n, ", ".join("`%s`" % x for x in libs) if libs else "**no library on the floppies**"))
    out.append("")
    out.append("## All names\n")
    out.append("```")
    for n in sorted(where):
        libs = sorted(where[n])
        shown = ", ".join(libs[:6]) + (" (+%d more)" % (len(libs) - 6) if len(libs) > 6 else "")
        out.append("%-10s %s" % (n, shown))
    out.append("```\n")
    open(path, "w", encoding="utf-8", newline="\n").write("\n".join(out))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--archive", required=True, help="checkout of the norskdata-software-archive repository")
    ap.add_argument("--out", required=True, help="folder to write the two .md files into")
    args = ap.parse_args()
    found, stats = scan(args.archive)
    os.makedirs(args.out, exist_ok=True)
    write_entry_doc(os.path.join(args.out, "LINK-LIBRARY-ENTRY-POINTS.md"), found, stats)
    lookfor = ["INBT", "OUTBT", "INCH", "OUTCH", "ECHOM", "MON1", "MON2", "8ENTR", "8LEAV", "8RLDN", "8ERR",
               "5ENTR", "5ERET", "5LEAV", "5INIT", "STAT", "FORTRAN", "CLOCK", "DESCF", "EESCF", "RSIO"]
    write_index_doc(os.path.join(args.out, "LINK-LIBRARY-NAME-INDEX.md"), found, lookfor)
    print("images %d, NDFS volumes %d, :BRF files %d, distinct %d" % (
        stats["images"], stats["opened"], stats["brf_files"], len(found)))


if __name__ == "__main__":
    main()
