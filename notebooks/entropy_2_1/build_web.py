#!/usr/bin/env python3
"""Build browser-only viewer and editor versions of the entropy notebook."""
from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parent
SUPPORT_FILES = (
    "lab_support.py",
    "presentation.py",
    "proof_help.py",
    "scientific.py",
    "proofs/Entropy.lean",
    "proofs/verification.json",
)


def build(output: Path) -> None:
    output = output.resolve()
    with tempfile.TemporaryDirectory(prefix="entropy-wasm-") as temporary:
        stage = Path(temporary)
        shutil.copy2(ROOT / "entropy_2_1.py", stage / "entropy_2_1.py")
        shutil.copy2(ROOT / "notebook.css", stage / "notebook.css")
        public = stage / "public"

        for relative in SUPPORT_FILES:
            for base in (stage, public):
                destination = base / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(ROOT / relative, destination)

        def export(mode: str, destination: Path) -> None:
            subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "marimo",
                    "export",
                    "html-wasm",
                    str(stage / "entropy_2_1.py"),
                    "-o",
                    str(destination),
                    "--mode",
                    mode,
                    "--no-execute",
                    "--force",
                ],
                cwd=stage,
                check=True,
            )

        export("run", output)
        export("edit", output / "edit")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    build(parser.parse_args().output)
