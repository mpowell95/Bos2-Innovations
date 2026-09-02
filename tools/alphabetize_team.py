#!/usr/bin/env python3
"""
Sort the Boston 2 colleague lists by first name.

Both lists were already alphabetical — by surname. But they display the name
first-name-first ("Samuel Afari-Aikins"), so scanning down the left edge gives
Samuel, Nicole, Barbara, David, which reads as unsorted. Directory order is only
useful when the display shows it.

Sorting by the name as written makes the order visible. Ties on the first name
(two Farahs, two Matthews) fall back to the surname.

Two lists are reordered:

  * the "Boston 2 Team" roster in Meet Your Team, static <li> markup;
  * TEAM_CONTACTS, which builds the colleague picker in Build a Presentation.

Bio cards in the presentation are left alone. They sort by seniority and then by
dataset.name, which already begins with the first name, so within each rank they
are first-name ordered.

Usage:
    python3 alphabetize_team.py IN.html OUT.html
"""

import argparse
import re
import sys


def key_for(display):
    """Sort on the name as displayed: first name, then surname to break ties."""
    name = display.split("—")[0]
    name = re.sub(r"&[a-z]+;|&#\d+;", "", name)       # entities
    name = re.sub(r",.*", "", name).strip()            # drop credentials
    parts = name.split()
    if not parts:
        return ("", "")
    return (parts[0].lower(), parts[-1].lower())


def strip_tags(s):
    return " ".join(re.sub(r"<[^>]+>", " ", s).split())


def sort_roster(html):
    body_at = html.find("<body")
    m = re.search(
        r'(<ul[^>]*class="[^"]*team-raw-list[^"]*"[^>]*>)(.*?)(</ul>)',
        html[body_at:], re.S)
    if not m:
        sys.exit("could not find the team-raw-list roster")

    open_tag, inner, close_tag = m.group(1), m.group(2), m.group(3)
    items = re.findall(r"<li>.*?</li>", inner, re.S)
    if not items:
        sys.exit("roster has no <li> entries")

    def display(li):
        spans = re.findall(r"<span[^>]*>(.*?)</span>", li, re.S)
        return strip_tags(spans[0] if spans else li)

    before = [display(x) for x in items]
    items.sort(key=lambda li: key_for(display(li)))
    after = [display(x) for x in items]

    rebuilt = open_tag + "\n" + "\n".join(items) + "\n" + close_tag
    start = body_at + m.start()
    end = body_at + m.end()
    return html[:start] + rebuilt + html[end:], before, after


def sort_contacts(html):
    m = re.search(r"(const TEAM_CONTACTS\s*=\s*\[)(.*?)(\];)", html, re.S)
    if not m:
        sys.exit("could not find TEAM_CONTACTS")

    entries = re.findall(r"\{id:.*?\}", m.group(2), re.S)
    if not entries:
        sys.exit("TEAM_CONTACTS has no entries")

    def label(e):
        lm = re.search(r"label:\s*'([^']*)'", e)
        return lm.group(1) if lm else ""

    before = [label(e) for e in entries]
    entries.sort(key=lambda e: key_for(label(e)))
    after = [label(e) for e in entries]

    rebuilt = m.group(1) + "\n" + ",\n".join(entries) + "\n" + m.group(3)
    return html[:m.start()] + rebuilt + html[m.end():], before, after


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("output")
    args = ap.parse_args()

    html = open(args.input, encoding="utf-8").read()
    before_len = len(html)

    html, r_before, r_after = sort_roster(html)
    html, c_before, c_after = sort_contacts(html)

    if sorted(r_before) != sorted(r_after) or len(r_before) != len(r_after):
        sys.exit("roster lost or gained an entry; refusing to write")
    if sorted(c_before) != sorted(c_after) or len(c_before) != len(c_after):
        sys.exit("picker lost or gained an entry; refusing to write")

    print(f"roster: {len(r_after)} entries reordered")
    print(f"picker: {len(c_after)} entries reordered")
    print("\nnew order:")
    for n in r_after:
        print("   ", n)

    open(args.output, "w", encoding="utf-8").write(html)
    print(f"\n{before_len/1e6:.2f}M -> {len(html)/1e6:.2f}M chars")
    return 0


if __name__ == "__main__":
    sys.exit(main())
