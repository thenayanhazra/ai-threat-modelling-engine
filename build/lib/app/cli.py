"""Command-line interface: analyse a file without running the API server.

    threat-model analyze examples/payments-platform.yaml --kind kubernetes \
        --title "Payments Platform" --json model.json --pdf model.pdf
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from app.engine import analyze
from app.models import SourceKind
from app.parsers import parse_input
from app.report import render_pdf


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="threat-model", description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    a = sub.add_parser("analyze", help="build a threat model from a diagram or IaC file")
    a.add_argument("file", type=Path)
    a.add_argument("--kind", choices=[k.value for k in SourceKind], help="input type (default: detect)")
    a.add_argument("--title", default="Infrastructure Threat Model")
    a.add_argument("--json", type=Path, help="write the threat model as JSON")
    a.add_argument("--pdf", type=Path, help="write the executive PDF report")
    args = parser.parse_args(argv)

    data = args.file.read_bytes()
    kind = SourceKind(args.kind) if args.kind else None
    model = analyze(parse_input(args.file.name, data, kind), args.title)

    if args.json:
        args.json.write_text(model.model_dump_json(indent=2))
    if args.pdf:
        args.pdf.write_bytes(render_pdf(model))
    if not args.json and not args.pdf:
        sys.stdout.write(model.model_dump_json(indent=2) + "\n")
    else:
        counts: dict[str, int] = {}
        for f in model.findings:
            counts[f.severity] = counts.get(f.severity, 0) + 1
        summary = ", ".join(f"{n} {s}" for s, n in sorted(counts.items()))
        print(f"{len(model.findings)} findings ({summary}); {len(model.attack_paths)} attack paths")
    return 0


if __name__ == "__main__":
    sys.exit(main())
