#!/usr/bin/env python3
"""Rewrite {{baseUrl}}/api/<version>/ references produced by `bru import openapi`
into {{url}}/{{version}}/, to match the variables already defined in the Bruno
environment (drf-spectacular has no notion of a base host, and `bru` has no
notion of our version prefix, so neither tool can produce this split alone).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path


def rewrite_file(path: Path, old_prefix: str, new_prefix: str) -> bool:
    content = path.read_text()
    if old_prefix not in content:
        return False
    path.write_text(content.replace(old_prefix, new_prefix))
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("collection_dir", type=Path)
    parser.add_argument("--api-version", default="v1")
    args = parser.parse_args()

    old_prefix = "{{baseUrl}}/api/" + args.api_version + "/"
    new_prefix = "{{url}}/{{version}}/"

    changed = 0
    for bru_file in args.collection_dir.rglob("*.bru"):
        if rewrite_file(bru_file, old_prefix, new_prefix):
            changed += 1

    print(f"Rewrote {changed} file(s) under {args.collection_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
