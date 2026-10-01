"""Link rewriting for a site whose docs_dir is the whole repository.

MkDocs only knows the Markdown pages. A relative link in a page can also point at
  - a folder                      -> the folder's README.md if it is a page, else the folder on GitHub
  - a file that is not a page     -> that file on GitHub (binaries, sources, scripts are not on the site)
  - nothing at all                -> left untouched, so MkDocs warns and --strict fails (a real broken link)
Links are rewritten in the Markdown source before MkDocs resolves them, including raw HTML href="...".
"""
import logging
import os
import re
from urllib.parse import quote, unquote

log = logging.getLogger("mkdocs.hooks.links")

REPO_URL = "https://github.com/RetroCoreLabs/NDInsight"
BRANCH = "main"

_pages = set()
_root = None

# [text](target "title")  /  [text](<target with spaces>)  /  href="target"
_MD_LINK = re.compile(r'(\]\()(<[^>]+>|[^)\s]+(?: [^)"]*?)?)((?:\s+"[^"]*")?\))')
_HTML_HREF = re.compile(r'(\bhref\s*=\s*")([^"]+)(")')


def on_files(files, config):
    global _root
    _root = os.path.abspath(config["docs_dir"])
    _pages.clear()
    for f in files:
        if f.is_documentation_page():
            _pages.add(f.src_uri)
    return files


def _rewrite(target, page_src):
    raw = target[1:-1] if target.startswith("<") else target
    if re.match(r"^([a-zA-Z][a-zA-Z0-9+.-]*:|#|//|/)", raw):
        return None
    path, sep, frag = raw.partition("#")
    path, qsep, query = path.partition("?")
    if not path:
        return None
    rel = unquote(path)
    base = os.path.dirname(page_src)
    joined = os.path.normpath(os.path.join(base, rel)).replace("\\", "/")
    if joined.startswith(".."):
        return None
    if joined in _pages:
        return None
    full = os.path.join(_root, joined)
    if os.path.isdir(full):
        readme = (joined + "/README.md") if joined != "." else "README.md"
        if readme in _pages:
            return quote(os.path.relpath(readme, base or ".").replace("\\", "/")) + (sep + frag if sep else "")
        return "%s/tree/%s/%s" % (REPO_URL, BRANCH, quote(joined))
    if os.path.isfile(full):
        return "%s/blob/%s/%s" % (REPO_URL, BRANCH, quote(joined)) + (sep + frag if sep else "")
    return None


def on_page_markdown(markdown, page, config, files):
    src = page.file.src_uri

    def md_sub(m):
        new = _rewrite(m.group(2), src)
        return m.group(0) if new is None else m.group(1) + new + m.group(3)

    def html_sub(m):
        new = _rewrite(m.group(2), src)
        return m.group(0) if new is None else m.group(1) + new + m.group(3)

    markdown = _MD_LINK.sub(md_sub, markdown)
    return _HTML_HREF.sub(html_sub, markdown)
