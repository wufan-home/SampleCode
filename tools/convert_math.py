#!/usr/bin/env python3
r"""Normalize LaTeX math delimiters in Markdown files.

1. Inline math  \( ... \)  ->  $$ ... $$
2. Display math \[ ... \]  ->  a block with each $$ on its own line:

       $$
       ...
       $$

   This is what Jekyll/kramdown passes to MathJax (the post needs `math: true`),
   and github.com renders it too. Multi-line formulas that use \\ line breaks
   are wrapped in \begin{gathered} ... \end{gathered}, because MathJax 3 ignores
   a bare \\ in display math. (--display fence emits ```math blocks instead;
   those render on github.com only, not on a Jekyll site.)
3. Lines that contain only ------ are removed.

Fenced code blocks, inline `code` spans and YAML front matter are left untouched.
A delimiter without its partner is left as is and reported.

Usage:
    python3 convert_math.py FILE_OR_DIR ...            # rewrite files in place
    python3 convert_math.py --check FILE_OR_DIR ...    # only show what would change
    python3 convert_math.py --display fence ...        # emit ```math blocks instead of $$
Directories are searched recursively for *.md / *.markdown files.
"""
import argparse
import difflib
import os
import re
import sys

FENCE = re.compile(r'^[ \t]*(`{3,}|~{3,})')
RULE = re.compile(r'^[ \t]*------[ \t]*$')
INLINE_CODE = re.compile(r'(`+)(?:(?!\1).)+?\1', re.S)
LIST_MARKER = re.compile(r'^([ \t]*)([-*+]|\d+[.)])([ \t]+)')
OPEN_DISPLAY = re.compile(r'(?<!\\)\\\[')
CLOSE_DISPLAY = re.compile(r'(?<!\\)\\\]')
INLINE_MATH = re.compile(r'(?<!\\)\\\((.+?)(?<!\\)\\\)', re.S)


def split_runs(text):
    """Yield (is_protected, chunk) pieces: front matter and fenced code are protected."""
    lines = text.splitlines(keepends=True)
    i, buf = 0, []
    if lines and lines[0].strip() == '---':          # YAML front matter
        for j in range(1, len(lines)):
            if lines[j].strip() in ('---', '...'):
                yield True, ''.join(lines[:j + 1])
                i = j + 1
                break
    while i < len(lines):
        m = FENCE.match(lines[i])
        if not m:
            buf.append(lines[i]); i += 1; continue
        if buf:
            yield False, ''.join(buf); buf = []
        tok = m.group(1)
        j = i + 1
        while j < len(lines) and not re.match(r'^[ \t]*' + re.escape(tok[0]) + '{%d,}[ \t]*$' % len(tok), lines[j]):
            j += 1
        yield True, ''.join(lines[i:j + 1])          # an unclosed fence runs to EOF, as in Markdown
        i = j + 1
    if buf:
        yield False, ''.join(buf)


def convert_run(text, display, warnings, lineno):
    saved = []

    def hold(s):
        saved.append(s)
        return '\x00%d\x00' % (len(saved) - 1)

    text = INLINE_CODE.sub(lambda m: hold(m.group(0)), text)

    # --- display math: \[ ... \] -> fenced block on its own lines
    open_tok, close_tok = ('```math', '```') if display == 'fence' else ('$$', '$$')
    pos = 0
    while True:
        o = OPEN_DISPLAY.search(text, pos)
        if not o:
            break
        c = CLOSE_DISPLAY.search(text, o.end())
        if not c:
            warnings.append('line %d: \\[ without a closing \\]' % (lineno + text.count('\n', 0, o.start())))
            break
        line_start = text.rfind('\n', 0, o.start()) + 1
        line_end = text.find('\n', c.end())
        line_end = len(text) if line_end < 0 else line_end
        prefix, body, suffix = text[line_start:o.start()], text[o.end():c.start()], text[c.end():line_end]

        lm = LIST_MARKER.match(prefix)
        marker_only = bool(lm) and not prefix[lm.end():].strip()
        indent = ' ' * len(lm.group(0)) if lm else re.match(r'[ \t]*', prefix).group(0)
        body_lines = [l.strip() for l in body.strip().split('\n')]
        if display == 'dollars' and '\\\\' in body and '\\begin{' not in body:
            body_lines = ['\\begin{gathered}'] + body_lines + ['\\end{gathered}']
        block = [indent + open_tok] + [indent + l if l else '' for l in body_lines] + [indent + close_tok]

        pieces = []
        if marker_only:                      # "- \[ x \]": open the block on the list-marker line
            block[0] = lm.group(0) + open_tok
        elif prefix.strip():
            pieces += [prefix.rstrip(), '']
        elif line_start > 0 and text[:line_start - 1].rsplit('\n', 1)[-1].strip():
            pieces += ['']                   # blank line between a paragraph and the block
        pieces += block
        rest = suffix.strip()
        tail = text[line_end:]
        if rest:
            replacement = hold('\n'.join(pieces)) + '\n\n' + indent + rest
        else:
            replacement = hold('\n'.join(pieces))
            if tail.startswith('\n') and tail[1:].split('\n', 1)[0].strip():
                replacement += '\n'          # blank line between the block and the next paragraph
        text = text[:line_start] + replacement + tail
        pos = line_start + len(replacement) - (len(indent + rest) if rest else 0)  # rescan the leftover text

    # --- inline math: \( ... \) -> $$ ... $$
    text = INLINE_MATH.sub(lambda m: '$$' + m.group(1).strip() + '$$', text)
    for m in re.finditer(r'(?<!\\)\\[()]', text):
        warnings.append('line %d: unpaired %s' % (lineno + text.count('\n', 0, m.start()), m.group(0)))

    # --- remove ------ lines
    kept, lines = [], text.splitlines(keepends=True)
    skip_blank = False
    for k, l in enumerate(lines):
        if RULE.match(l):
            # avoid leaving two blank lines where the rule used to be
            skip_blank = bool(kept) and not kept[-1].strip()
            continue
        if skip_blank and not l.strip():
            skip_blank = False
            continue
        skip_blank = False
        kept.append(l)
    text = ''.join(kept)

    while '\x00' in text:
        text = re.sub(r'\x00(\d+)\x00', lambda m: saved[int(m.group(1))], text)
    return text


def convert(text, display='dollars'):
    warnings, out, lineno = [], [], 1
    for protected, chunk in split_runs(text):
        out.append(chunk if protected else convert_run(chunk, display, warnings, lineno))
        lineno += chunk.count('\n')
    return ''.join(out), warnings


def iter_files(paths):
    for p in paths:
        if os.path.isdir(p):
            for root, dirs, files in os.walk(p):
                dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ('_site', 'node_modules')]
                for f in sorted(files):
                    if f.endswith(('.md', '.markdown')):
                        yield os.path.join(root, f)
        else:
            yield p


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('paths', nargs='+')
    ap.add_argument('--check', action='store_true', help='show a diff, do not write')
    ap.add_argument('--display', choices=['dollars', 'fence'], default='dollars',
                    help='output for \\[ \\]: $$ block (default) or ```math block')
    a = ap.parse_args()
    changed = 0
    for f in iter_files(a.paths):
        src = open(f, encoding='utf-8').read()
        dst, warnings = convert(src, a.display)
        for w in warnings:
            print('%s: warning: %s (left unchanged)' % (f, w), file=sys.stderr)
        if dst == src:
            continue
        changed += 1
        if a.check:
            sys.stdout.writelines(difflib.unified_diff(src.splitlines(True), dst.splitlines(True), f, f + ' (converted)'))
        else:
            open(f, 'w', encoding='utf-8').write(dst)
            print('converted', f)
    print('%d file(s) %s' % (changed, 'would change' if a.check else 'changed'), file=sys.stderr)


if __name__ == '__main__':
    main()
