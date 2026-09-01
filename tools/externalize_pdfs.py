#!/usr/bin/env python3
"""
Replace embedded PDF attachments with links to where the file actually lives.

The toolkit's resources table links eight documents to SharePoint but embedded
two as `data:application/pdf` payloads, which cost 1.55M characters — around a
tenth of the whole file. They are also the least likely links to work once
hosted: the host's CSP does not allow `data:`, and browsers block top-level
navigation to a data: URL regardless.

Swapping them for ordinary links reclaims the space and matches how every other
document in that table is handled.

Usage:
    python3 externalize_pdfs.py IN.html OUT.html \
        --link Initial-Wealth-Forecast-Plan-Preparation.pdf=https://... \
        --link Add-Accounts-Guide.pdf=https://...

The key of each --link is the anchor's `download` filename.
"""

import argparse
import re
import sys

# <a href="data:application/pdf;base64,...." download="Name.pdf">Download PDF</a>
ANCHOR = re.compile(
    r'<a\s+href="data:application/pdf;base64,[A-Za-z0-9+/=]+"\s+'
    r'download="(?P<name>[^"]+)"\s*>(?P<text>.*?)</a>',
    re.S,
)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("output")
    ap.add_argument("--link", action="append", default=[], metavar="FILENAME=URL")
    ap.add_argument("--text", default="Open PDF",
                    help="anchor label (default: Open PDF, since it now opens rather than downloads)")
    args = ap.parse_args()

    links = {}
    for pair in args.link:
        if "=" not in pair:
            sys.exit(f"--link needs FILENAME=URL, got: {pair}")
        name, url = pair.split("=", 1)
        links[name.strip()] = url.strip()

    html = open(args.input, encoding="utf-8").read()
    before = len(html)
    seen, saved = [], [0]

    def repl(m):
        name = m.group("name")
        if name not in links:
            return m.group(0)
        seen.append(name)
        saved[0] += len(m.group(0))
        # target="_blank" matches how the other eight documents are linked.
        return f'<a href="{links[name]}" target="_blank">{args.text}</a>'

    html = ANCHOR.sub(repl, html)

    missing = set(links) - set(seen)
    if missing:
        sys.exit("never found an embedded anchor for: " + ", ".join(sorted(missing)))

    open(args.output, "w", encoding="utf-8").write(html)
    for n in seen:
        print(f"  linked out: {n}")
    left = len(re.findall(r"data:application/pdf;base64,", html))
    print(f"\n{before/1e6:.2f}M -> {len(html)/1e6:.2f}M chars "
          f"(freed {saved[0]/1e6:.2f}M)")
    print(f"embedded PDFs remaining: {left}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
