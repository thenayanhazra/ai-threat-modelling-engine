import json
from pathlib import Path

from app.cli import main

EXAMPLE = Path(__file__).resolve().parent.parent / "examples" / "payments-platform.yaml"


def test_cli_writes_json_and_pdf(tmp_path: Path) -> None:
    out_json, out_pdf = tmp_path / "m.json", tmp_path / "m.pdf"
    rc = main(["analyze", str(EXAMPLE), "--kind", "kubernetes", "--json", str(out_json), "--pdf", str(out_pdf)])
    assert rc == 0
    model = json.loads(out_json.read_text())
    assert model["findings"] and model["attack_paths"]
    assert out_pdf.read_bytes().startswith(b"%PDF")
