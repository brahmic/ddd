#!/usr/bin/env python3
"""Check this guide's inline links, ATX headings and triple-backtick PHP blocks."""

from pathlib import Path
import re
import shutil
import subprocess
import sys
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parent.parent
FENCE = re.compile(r"^```([^\n]*)\n(.*?)^```[ \t]*$", re.M | re.S)
HEADING = re.compile(r"^#{1,6}[ \t]+(.+)$", re.M)
LINK = re.compile(r"\[[^\]\n]*\]\(([^)\n]+)\)")
RULE = re.compile(r"(?:DDD|ARCH|TEST|LAR)-[A-Z]+-\d+")


def main():
    php = shutil.which("php")
    if php is None:
        sys.exit("PHP CLI 8.3+ is required to check the examples.")
    version = subprocess.run(
        [php, "-n", "-r", "exit(PHP_VERSION_ID >= 80300 ? 0 : 1);"],
        capture_output=True, text=True,
    )
    if version.returncode:
        sys.exit("PHP CLI 8.3+ is required to check the examples.")

    files = sorted(
        path for path in ROOT.rglob("*.md")
        if not any(part.startswith(".") or part in {"vendor", "node_modules"}
                   for part in path.relative_to(ROOT).parts)
    )
    if not files:
        sys.exit("No Markdown files found.")

    documents, anchors, rules = {}, {}, {}
    errors = []
    link_count = php_count = 0

    for path in files:
        raw = path.read_text(encoding="utf-8")
        label = path.relative_to(ROOT)
        # Preserve line numbers while excluding code from links and headings.
        prose = FENCE.sub(lambda match: re.sub(r"[^\n]", " ", match[0]), raw)
        documents[path] = prose
        anchors[path] = set()
        if len(re.findall(r"^```[^\n]*$", raw, re.M)) % 2:
            errors.append(f"{label}: unclosed code fence")

        for match in HEADING.finditer(prose):
            title = re.sub(r"\s+#+\s*$", "", match[1]).strip()
            line = prose.count("\n", 0, match.start()) + 1
            slug = re.sub(r"[^\w\- ]", "", title.lower()).replace(" ", "-")
            anchor, suffix = slug, 0
            while anchor in anchors[path]:
                suffix += 1
                anchor = f"{slug}-{suffix}"
            anchors[path].add(anchor)
            if RULE.fullmatch(title):
                if title in rules:
                    errors.append(f"{label}:{line}: duplicate {title}; first at {rules[title]}")
                else:
                    rules[title] = f"{label}:{line}"

        for match in FENCE.finditer(raw):
            if match[1].strip() != "php":
                continue
            php_count += 1
            line = raw.count("\n", 0, match.start()) + 1
            result = subprocess.run(
                [php, "-n", "-l"], input=match[2], capture_output=True, text=True,
            )
            if result.returncode:
                detail = (result.stdout + result.stderr).strip()
                errors.append(f"{label}:{line}: PHP syntax error\n{detail}")

    for path, prose in documents.items():
        for match in LINK.finditer(prose):
            target = match[1]
            url = urlsplit(target)
            if url.scheme or url.netloc:
                continue
            link_count += 1
            destination = (path.parent / unquote(url.path)).resolve()
            if not url.path:
                destination = path
            label = path.relative_to(ROOT)
            line = prose.count("\n", 0, match.start()) + 1
            if not destination.exists():
                errors.append(f"{label}:{line}: missing file: {target}")
            elif url.fragment and unquote(url.fragment) not in anchors.get(destination, set()):
                errors.append(f"{label}:{line}: missing anchor: {target}")

    print(f"Checked {len(files)} Markdown files, {link_count} local links, "
          f"{len(rules)} rule IDs and {php_count} PHP blocks.")
    for error in errors:
        print(error, file=sys.stderr)
    if errors:
        return 1
    print("Documentation checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
