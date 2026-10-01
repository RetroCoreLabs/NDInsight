# Contributing

## Docs site

The site at <https://retrocorelabs.github.io/ndinsight/> is built with MkDocs Material from
this repository (layout A: the repository is the docs folder). It is rebuilt and published by
`.github/workflows/docs.yml` on every push to `main`.
Settings, Pages, Source must be set to "GitHub Actions".

Build locally (the output folder must be OUTSIDE the checkout):

```bash
python3 -m venv ~/venvs/ndinsight-site
~/venvs/ndinsight-site/bin/pip install -r docs-site/requirements.txt
~/venvs/ndinsight-site/bin/mkdocs build -f docs-site/mkdocs.yml -d ~/ndinsight-site-out
```

The build takes about 3 minutes (2,500+ pages). Use `mkdocs serve -f docs-site/mkdocs.yml`
to preview.

### TODO: make the build strict

The CI build is currently NOT strict. A strict build fails on 860 warnings (measured on a
local build), all of them broken links in the documents:

- 520 links to images or other files that are not in the repository (many in the OCR'd manuals)
- 270 placeholder links such as `image` or `image-link-placeholder`
- 66 links to `.md` pages that do not exist (for example `Developer/NAVIGATION.md` links to `_START-HERE.md`)
- 4 absolute links

Some links also point into the XMSG working folders that `.gitignore` excludes.

To do:

1. List the warnings: run the build and read the `WARNING` lines (the CI run page also shows a summary).
2. Fix each link in the source document: restore or correct the target, or remove the link. Do not guess a missing image or page.
3. When the warning count is 0, change the build step in `.github/workflows/docs.yml` to `mkdocs build --strict`.
4. Run the build once in a fresh clone before pushing.

### Site size

The local build is 648 MB (GitHub Pages allows 1 GB). `.txt` and `.asm` files are excluded
from the site (`exclude_docs` in `docs-site/mkdocs.yml`); links to them point to the file on
GitHub (`docs-site/hooks.py`). That saved about 50 MB. What remains is mostly the HTML pages
(about 400 MB) and the search index (about 80 MB). If the site grows towards 1 GB, the next
candidates are the copied `.cs` and `.c` sources and the PDFs.
