#!/usr/bin/env python3
# Function Name: security_signal_scan, main
# Description: Scan source files for common security-risk signals to guide manual security review.

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


SHARED_SCRIPTS = Path(__file__).resolve().parents[2] / "_shared" / "scripts"
sys.path.insert(0, str(SHARED_SCRIPTS))

from signal_scan import build_signal_report, print_signal_report  # noqa: E402
from skill_common import BROAD_TEXT_EXTENSIONS  # noqa: E402


PATTERNS = [
    ("secret material", re.compile(r"(?i)(api[_-]?key|secret|token|password|private[_-]?key)\s*[:=]\s*['\"][^'\"]{8,}")),
    ("command execution", re.compile(r"\b(exec|spawn|system|popen|subprocess|ProcessBuilder|child_process)\b")),
    ("dynamic code execution", re.compile(r"\b(eval|execScript|new Function)\b")),
    ("unsafe deserialization", re.compile(r"\b(pickle\.loads|yaml\.load|marshal\.loads|joblib\.load|torch\.load|ObjectInputStream|readObject|unserialize)\b")),
    ("sql construction", re.compile(r"(?i)(select|insert|update|delete).*(\+|\$\{|%s|format\()")),
    ("html/script sink", re.compile(r"\b(innerHTML|dangerouslySetInnerHTML|document\.write|v-html)\b")),
    ("path traversal risk", re.compile(r"\b(open|readFile|writeFile|send_file|FileInputStream)\b.*(\.\.|path|filename|fileName)")),
    ("file upload handling", re.compile(r"(?i)\b(upload|multipart|multer|formidable|FileField|request\.FILES|UploadedFile|IFormFile)\b")),
    ("sensitive data logging", re.compile(r"(?i)\b(log|logger|console\.(log|warn|error)|print)\b.*\b(email|ssn|dob|phone|address|credit.?card|cardNumber|token|password)\b")),
    ("weak crypto", re.compile(r"\b(md5|sha1|DES|RC4|ECB)\b")),
    ("tls verification disabled", re.compile(r"(?i)(verify\s*=\s*false|rejectUnauthorized\s*:\s*false|InsecureSkipVerify)")),
    ("permissive cors", re.compile(r"(?i)(Access-Control-Allow-Origin.*\*|cors\(\s*\)|origin\s*:\s*['\"]\*['\"])")),
    ("debug mode", re.compile(r"(?i)(debug\s*=\s*true|DEBUG\s*=\s*True|app\.run\(.*debug=True)")),
]


def security_signal_scan(target: Path) -> dict[str, object]:
    return build_signal_report(target, PATTERNS, BROAD_TEXT_EXTENSIONS, __file__)


def main() -> int:
    parser = argparse.ArgumentParser(description="Scan files for security-review signals.")
    parser.add_argument("target", nargs="?", default=".", help="File or directory to scan.")
    args = parser.parse_args()

    target = Path(args.target).resolve()
    if not target.exists():
        print(f"target not found: {target}", file=sys.stderr)
        return 1

    print_signal_report(
        "security signal scan",
        security_signal_scan(target),
        "note: signals are non-exhaustive line-based review prompts, not confirmed vulnerabilities; source comments are skipped, but strings and docs may still match",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
