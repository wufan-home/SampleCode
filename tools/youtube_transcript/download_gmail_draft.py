#!/usr/bin/env python3.9
"""
download_drafts.py
 
Read every item in a Google Takeout "Drafts" mailbox and write each draft to a
its own .txt file.
 
Requirements satisfied:
    1. Source is a Google Takeout Mail export. --source may point at either the
       export FOLDER (the script finds the Drafts mbox inside it) or directly at
       a specific .mbox FILE. Default folder:
           /Users/fanwu/Downloads/deepexploring
    2. The output folder is chosen on the command line with -o / --output.
    3. The source is chosen on the command line with -s / --source.
    4. Each draft is written to a .txt file:
         - file NAME    = a short summary of the draft
                          (its Subject; or, if it has none, the first line of
                          the body). Made unique with a numeric suffix so
                          nothing is silently overwritten.
         - file CONTENT = the draft's body text (the text/plain part if present,
                          otherwise the HTML part with tags stripped).
 
Uses only the Python standard library -- no pip installs required.
 
Usage:
    python3.9 download_drafts.py -s /path/to/Drafts.mbox -o /path/to/out
    python3.9 download_drafts.py --source /Users/fanwu/Downloads/deepexploring \
                                 --output ./drafts_txt
    python3.9 download_drafts.py            # uses the defaults below
"""
 
import argparse
import email
import email.header
import html
import mailbox
import os
import re
import sys
 
# ----------------------------------------------------------------------------
# Defaults (overridable on the command line)
# ----------------------------------------------------------------------------
DEFAULT_SOURCE = "/Users/fanwu/Downloads/deepexploring"
DEFAULT_OUTPUT = "./drafts_txt"
 
SUMMARY_MAX_LEN = 80   # max characters used from the body when there's no subject
 
 
# ----------------------------------------------------------------------------
# Locating the source mailbox
# ----------------------------------------------------------------------------
def resolve_source(path):
    """Locate the mbox file to open and decide whether to filter by label.
 
    Returns a tuple (mbox_file, dedicated_drafts).
      * dedicated_drafts is True when every message in the file should be
        treated as a draft (a Drafts-only mbox), so no label filtering is
        applied.
      * dedicated_drafts is False for a combined Takeout export (e.g.
        "All mail Including Spam and Trash.mbox"), where only messages whose
        X-Gmail-Labels header includes "Draft" are kept.
 
    `path` may be:
      * a direct .mbox file            -> used as-is
      * an Apple Mail ".mbox" bundle   -> its inner "mbox" file
      * a Takeout export folder        -> a Drafts mbox if present, otherwise
                                          the single combined mbox inside it
    """
    if os.path.isfile(path):
        return path, ("draft" in os.path.basename(path).lower())
 
    if os.path.isdir(path):
        # Apple Mail bundle: a folder that directly contains an "mbox" file.
        inner = os.path.join(path, "mbox")
        if os.path.isfile(inner):
            return inner, ("draft" in os.path.basename(path).lower())
 
        # Takeout folder: collect every .mbox, splitting out drafts-named ones.
        drafts = []
        others = []
        for root, _dirs, files in os.walk(path):
            for f in files:
                if f.lower().endswith(".mbox"):
                    full = os.path.join(root, f)
                    if "draft" in f.lower():
                        drafts.append(full)
                    else:
                        others.append(full)
 
        # 1) A dedicated Drafts mailbox is the ideal case.
        if len(drafts) == 1:
            return drafts[0], True
        if len(drafts) > 1:
            sys.exit(
                "ERROR: found several drafts mailboxes; pass one explicitly "
                "with --source:\n  " + "\n  ".join(sorted(drafts))
            )
 
        # 2) No drafts-named file. If there is exactly ONE other mbox (e.g. the
        #    combined "All mail ...mbox"), use it and filter by the Draft label.
        if len(others) == 1:
            return others[0], False
        if len(others) > 1:
            sys.exit(
                "ERROR: multiple mailboxes found and none is named 'Draft'. "
                "Point --source at the exact file:\n  "
                + "\n  ".join(sorted(others))
            )
        sys.exit("ERROR: no .mbox files found under '%s'." % path)
 
    sys.exit("ERROR: source not found at '%s'." % path)
 
 
def is_draft_message(message, dedicated_drafts):
    """Decide whether a message should be treated as a draft.
 
    For a dedicated Drafts mbox, every message qualifies. For a combined
    Takeout export, Gmail records the folder in the 'X-Gmail-Labels' header;
    drafts carry the "Draft" label there.
    """
    if dedicated_drafts:
        return True
    labels = message.get("X-Gmail-Labels")
    if not labels:
        return False
    tokens = [t.strip().lower() for t in decode_mime_words(labels).split(",")]
    return "draft" in tokens
 
 
# ----------------------------------------------------------------------------
# Header / body helpers
# ----------------------------------------------------------------------------
def decode_mime_words(value):
    """Decode an RFC 2047 encoded header (e.g. a subject) into a clean string."""
    if not value:
        return ""
    parts = []
    for text, charset in email.header.decode_header(value):
        if isinstance(text, bytes):
            try:
                parts.append(text.decode(charset or "utf-8", errors="replace"))
            except (LookupError, TypeError):
                parts.append(text.decode("utf-8", errors="replace"))
        else:
            parts.append(text)
    return "".join(parts)
 
 
def part_to_text(part):
    """Decode a single message part's payload to text using its charset."""
    payload = part.get_payload(decode=True)
    if payload is None:
        return ""
    charset = part.get_content_charset() or "utf-8"
    try:
        return payload.decode(charset, errors="replace")
    except (LookupError, TypeError):
        return payload.decode("utf-8", errors="replace")
 
 
def html_to_text(raw_html):
    """Very small HTML-to-text: drop scripts/styles, tags, unescape entities."""
    raw_html = re.sub(r"(?is)<(script|style).*?</\1>", "", raw_html)
    raw_html = re.sub(r"(?i)<br\s*/?>", "\n", raw_html)
    raw_html = re.sub(r"(?i)</p\s*>", "\n\n", raw_html)
    text = re.sub(r"(?s)<[^>]+>", "", raw_html)
    text = html.unescape(text)
    # Collapse excessive blank lines.
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()
 
 
def extract_body(message):
    """Return the best-effort plain-text body of a message.
 
    Prefers a text/plain part; falls back to a text/html part (tags stripped).
    """
    plain_chunks = []
    html_chunks = []
 
    for part in message.walk():
        if part.is_multipart():
            continue
        content_type = (part.get_content_type() or "").lower()
        # Skip anything that is an attachment rather than the message text.
        disposition = (part.get("Content-Disposition") or "").lower()
        if "attachment" in disposition:
            continue
        if content_type == "text/plain":
            plain_chunks.append(part_to_text(part))
        elif content_type == "text/html":
            html_chunks.append(part_to_text(part))
 
    if plain_chunks:
        return "\n".join(c for c in plain_chunks if c).strip()
    if html_chunks:
        return html_to_text("\n".join(html_chunks))
    return ""
 
 
def make_summary(subject, body):
    """Build a short summary string for use as the filename."""
    subject = (subject or "").strip()
    if subject:
        return subject
    # No subject -> use the first non-empty line of the body.
    for line in (body or "").splitlines():
        line = line.strip()
        if line:
            if len(line) > SUMMARY_MAX_LEN:
                line = line[:SUMMARY_MAX_LEN].rstrip() + "..."
            return line
    return "untitled_draft"
 
 
# ----------------------------------------------------------------------------
# Filesystem helpers
# ----------------------------------------------------------------------------
def sanitize_filename(name):
    """Turn a summary into a safe filesystem filename (no extension)."""
    if not name:
        name = "untitled_draft"
    name = re.sub(r'[\\/*?:"<>|\r\n\t]', "_", name)
    name = re.sub(r"\s+", " ", name).strip()
    name = name.rstrip(". ")
    if not name:
        name = "untitled_draft"
    return name[:180]
 
 
def unique_path(directory, base_name, ext=".txt"):
    """Return a non-colliding path for base_name+ext inside directory."""
    candidate = os.path.join(directory, base_name + ext)
    if not os.path.exists(candidate):
        return candidate
    i = 2
    while True:
        candidate = os.path.join(directory, "%s (%d)%s" % (base_name, i, ext))
        if not os.path.exists(candidate):
            return candidate
        i += 1
 
 
# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------
def parse_args():
    parser = argparse.ArgumentParser(
        description="Write each draft in a Google Takeout Drafts mbox to a .txt "
                    "file named after a short summary of the draft."
    )
    parser.add_argument(
        "-s", "--source", default=DEFAULT_SOURCE,
        help="Takeout export folder OR a specific .mbox file. Default: %s"
             % DEFAULT_SOURCE,
    )
    parser.add_argument(
        "-o", "--output", default=DEFAULT_OUTPUT,
        help="Folder to write the .txt files into (created if missing). "
             "Default: %s" % DEFAULT_OUTPUT,
    )
    return parser.parse_args()
 
 
def main():
    args = parse_args()
    mbox_file, dedicated_drafts = resolve_source(os.path.expanduser(args.source))
    output_dir = os.path.abspath(os.path.expanduser(args.output))
    os.makedirs(output_dir, exist_ok=True)
 
    print("Reading drafts from: %s" % mbox_file)
    if not dedicated_drafts:
        print("  (combined mailbox -> keeping only messages labeled 'Draft')")
    print("Writing .txt files to: %s\n" % output_dir)
 
    mbox = mailbox.mbox(mbox_file, factory=None)
 
    scanned = 0
    written = 0
    for key, message in mbox.iteritems():
        scanned += 1
        if not is_draft_message(message, dedicated_drafts):
            continue
 
        subject = decode_mime_words(message.get("Subject", ""))
        body = extract_body(message)
        summary = make_summary(subject, body)
        safe_name = sanitize_filename(summary)
 
        out_path = unique_path(output_dir, safe_name, ".txt")
        with open(out_path, "w", encoding="utf-8") as fh:
            fh.write(body)
 
        written += 1
        print("  ✓ %s" % os.path.basename(out_path))
 
    if not dedicated_drafts:
        print("\nDone. Wrote %d draft(s) (scanned %d message(s)) into:\n  %s"
              % (written, scanned, output_dir))
    else:
        print("\nDone. Wrote %d draft(s) into:\n  %s" % (written, output_dir))
 
    if written == 0:
        print(
            "\nNo drafts were written. If you expected some, the mailbox may "
            "not tag drafts with an 'X-Gmail-Labels: Draft' header -- run again "
            "pointing --source at a specific Drafts mbox, or tell me and I'll "
            "adjust the filter."
        )
 
 
if __name__ == "__main__":
    main()
 
