#!/usr/bin/env python3.9
"""
download_takeout_pdfs.py
 
Extract the PDF attachment(s) from every email in a Google Takeout mbox and
save each PDF using the email's subject as the filename.
 
Requirements satisfied:
    1. The saved PDF filename is the subject of the email that the PDF is
       attached to. (Duplicate subjects / multiple PDFs in one email are made
       unique with a numeric suffix so nothing is silently overwritten.)
    2. Source is a Google Takeout mailbox (a single flat mbox file), default:
           /Users/fanwu/Downloads/fanwu2017/Mail/Inbox.mbox
    3. The output folder is chosen on the command line with -o / --output.
    4. The source mbox file is chosen on the command line with -s / --source.
 
Uses only the Python standard library -- no pip installs required.
 
Usage:
    python3.9 download_takeout_pdfs.py -s /path/to/Inbox.mbox -o /path/to/out
    python3.9 download_takeout_pdfs.py --source Inbox.mbox --output ./pdfs
    python3.9 download_takeout_pdfs.py            # uses the defaults below
"""
 
import argparse
import email
import email.header
import mailbox
import os
import re
import sys
 
# ----------------------------------------------------------------------------
# Defaults (overridable on the command line)
# ----------------------------------------------------------------------------
DEFAULT_SOURCE = "/Users/fanwu/Downloads/fanwu2017/Mail/Inbox.mbox"
DEFAULT_OUTPUT = "./pdf_attachments"
 
 
# ----------------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------------
def resolve_mbox_path(path):
    """Return the actual mbox file to open.
 
    Google Takeout exports a plain flat mbox file, which is handled directly.
    As a convenience this also handles an Apple Mail ".mbox" bundle (a folder
    containing a file named "mbox"), in case a different source is passed.
    """
    if os.path.isfile(path):
        return path
    if os.path.isdir(path):
        inner = os.path.join(path, "mbox")
        if os.path.isfile(inner):
            return inner
        for root, _dirs, files in os.walk(path):
            if "mbox" in files:
                return os.path.join(root, "mbox")
        sys.exit(
            "ERROR: '%s' is a directory but no inner 'mbox' file was found."
            % path
        )
    sys.exit("ERROR: source mailbox not found at '%s'." % path)
 
 
def decode_mime_words(value):
    """Decode an RFC 2047 encoded header (e.g. subjects) into a clean string."""
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
 
 
def sanitize_filename(name):
    """Turn an email subject into a safe filesystem filename (no extension)."""
    if not name:
        name = "no_subject"
    # Replace characters that are illegal/awkward on common filesystems.
    name = re.sub(r'[\\/*?:"<>|\r\n\t]', "_", name)
    # Collapse whitespace and trim.
    name = re.sub(r"\s+", " ", name).strip()
    # Avoid names ending in a dot/space (problematic on Windows).
    name = name.rstrip(". ")
    if not name:
        name = "no_subject"
    return name[:180]
 
 
def unique_path(directory, base_name):
    """Return a non-colliding '.pdf' path for base_name inside directory."""
    candidate = os.path.join(directory, base_name + ".pdf")
    if not os.path.exists(candidate):
        return candidate
    i = 2
    while True:
        candidate = os.path.join(directory, "%s (%d).pdf" % (base_name, i))
        if not os.path.exists(candidate):
            return candidate
        i += 1
 
 
def is_pdf_part(part):
    """True if a message part is a PDF attachment."""
    content_type = (part.get_content_type() or "").lower()
    filename = part.get_filename()
    if filename:
        filename = decode_mime_words(filename)
    if content_type == "application/pdf":
        return True
    if content_type in ("application/octet-stream", "application/binary") \
            and filename and filename.lower().endswith(".pdf"):
        return True
    if filename and filename.lower().endswith(".pdf"):
        return True
    return False
 
 
# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------
def parse_args():
    parser = argparse.ArgumentParser(
        description="Extract PDF attachments from a Google Takeout mbox, "
                    "naming each PDF after its email subject."
    )
    parser.add_argument(
        "-s", "--source", default=DEFAULT_SOURCE,
        help="Path to the source mbox file. Default: %s" % DEFAULT_SOURCE,
    )
    parser.add_argument(
        "-o", "--output", default=DEFAULT_OUTPUT,
        help="Folder to write the PDFs into (created if it doesn't exist). "
             "Default: %s" % DEFAULT_OUTPUT,
    )
    return parser.parse_args()
 
 
def main():
    args = parse_args()
    mbox_file = resolve_mbox_path(os.path.expanduser(args.source))
    output_dir = os.path.abspath(os.path.expanduser(args.output))
    os.makedirs(output_dir, exist_ok=True)
 
    print("Reading mailbox: %s" % mbox_file)
    print("Writing PDFs to: %s\n" % output_dir)
 
    mbox = mailbox.mbox(mbox_file, factory=None)
 
    total_pdfs = 0
    emails_with_pdf = 0
 
    for key, message in mbox.iteritems():
        subject = decode_mime_words(message.get("Subject", ""))
        safe_subject = sanitize_filename(subject)
 
        found_pdf_in_email = False
        for part in message.walk():
            if part.is_multipart():
                continue
            if not is_pdf_part(part):
                continue
 
            payload = part.get_payload(decode=True)
            if payload is None:
                print("  ! Could not decode a PDF part in '%s'" % subject)
                continue
 
            out_path = unique_path(output_dir, safe_subject)
            with open(out_path, "wb") as fh:
                fh.write(payload)
 
            total_pdfs += 1
            found_pdf_in_email = True
            print("  ✓ Saved: %s" % os.path.basename(out_path))
 
        if found_pdf_in_email:
            emails_with_pdf += 1
 
    print(
        "\nDone. Extracted %d PDF(s) from %d email(s) into:\n  %s"
        % (total_pdfs, emails_with_pdf, output_dir)
    )
 
 
if __name__ == "__main__":
    main()
