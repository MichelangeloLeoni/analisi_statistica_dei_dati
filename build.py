#!/usr/bin/env python3
"""
Build script equivalent to the project Makefile.

Usage:
    python build.py              # same as 'make' (runs 'py' target)
    python build.py all          # same as 'make all'
    python build.py py           # run Python scripts, then build LaTeX
    python build.py build        # run latexmk directly
    python build.py production   # run scripts + build production PDF
    python build.py clean        # clean auxiliary files
    python build.py cleanall     # clean everything including PDFs
"""

import sys
import os
import glob
import subprocess
import shutil
import argparse
from pathlib import Path

# ── Configuration ──────────────────────────────────────────────────────────────

PYTHON    = sys.executable
SRC_DIR   = Path("src/asd/interval_estimation")
PY_DIR    = Path("scripts")
OUT_DIR   = Path(".build")
STAMP_DIR = Path(".stamps")

MAIN            = "analisi_statistica_dei_dati"
DRAFT_NAME      = "draft_analisi_statistica_dei_dati"
PRODUCTION_NAME = "production_analisi_statistica_dei_dati"

LATEXMK_BASE = [
    "latexmk", "-pdf",
    "-interaction=nonstopmode",
    "-halt-on-error",
    f"-auxdir={OUT_DIR}",
    "-outdir=.",    # minted v3 + MiKTeX needs explicit -outdir alongside -auxdir
    "-f",           # force rebuild even when latexmk thinks nothing changed
    "-silent",
    # minted v3 calls an external executable (latexminted) via \write18.
    # MiKTeX's default *restricted* shell escape blocks it — the log shows:
    #   runsystem(latexminted ...)...disabled (restricted).
    # -shell-escape upgrades to unrestricted shell escape so latexminted runs.
    "-pdflatex=pdflatex -shell-escape",
]

# Pass TEXMF_OUTPUT_DIRECTORY explicitly in the env of every latexmk call,
# mirroring what the Makefile does with  set TEXMF_OUTPUT_DIRECTORY=.build&& latexmk ...
# Using os.environ.copy() + explicit env= in subprocess ensures MiKTeX sees it
# on the very same invocation, regardless of any inherited shell state.
LATEX_ENV = os.environ.copy()
LATEX_ENV["TEXMF_OUTPUT_DIRECTORY"] = str(OUT_DIR)

# ── Helpers ────────────────────────────────────────────────────────────────────

def run(cmd: list[str], check: bool = True, latex: bool = False) -> int:
    """Run a shell command, printing it first.
    Pass latex=True to forward the TEXMF_OUTPUT_DIRECTORY env to MiKTeX."""
    print("$", " ".join(str(c) for c in cmd))
    env = LATEX_ENV if latex else None
    result = subprocess.run(cmd, env=env)
    if check and result.returncode != 0:
        sys.exit(result.returncode)
    return result.returncode


def clean_stale_fdb(jobname: str) -> None:
    """Delete the latexmk dependency database for a jobname.

    A failed previous run leaves a stale .fdb_latexmk which makes latexmk
    say 'Nothing to do' and replay the cached error instead of retrying.
    We remove it before every latexmk invocation so we always get a fresh run.
    The -f flag above is a second line of defence.
    """
    candidates = [
        Path(f"{jobname}.fdb_latexmk"),
        OUT_DIR / f"{jobname}.fdb_latexmk",
    ]
    for p in candidates:
        if p.exists():
            print(f"  Removing stale {p}")
            p.unlink()


def stamp_path(source: Path) -> Path:
    """Return the .stamp file path that corresponds to a source file."""
    return STAMP_DIR / (source.stem + ".stamp")


def needs_rebuild(source: Path, stamp: Path) -> bool:
    """Return True if the stamp is missing or older than the source."""
    if not stamp.exists():
        return True
    return source.stat().st_mtime > stamp.stat().st_mtime


def execute_script(source: Path) -> None:
    """Run a Python source file and write its stamp."""
    stamp = stamp_path(source)
    if not needs_rebuild(source, stamp):
        print(f"  (up to date) {source}")
        return

    STAMP_DIR.mkdir(parents=True, exist_ok=True)
    run([PYTHON, str(source)])
    stamp.write_text(f"Executed {source}\n")
    print(f"  Stamped   {stamp}")


def collect_sources() -> tuple[list[Path], list[Path]]:
    """Return (py_sources, src_sources) sorted for deterministic ordering."""
    py_sources  = sorted(PY_DIR.glob("*.py"))  if PY_DIR.exists()  else []
    src_sources = sorted(SRC_DIR.glob("*.py")) if SRC_DIR.exists() else []
    return py_sources, src_sources


# ── Targets ────────────────────────────────────────────────────────────────────

def target_py() -> None:
    """Run all Python scripts, then build the LaTeX document."""
    py_sources, src_sources = collect_sources()
    for src in py_sources + src_sources:
        execute_script(src)
    target_build()


def target_build() -> None:
    """Run latexmk on the main .tex file."""
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    clean_stale_fdb(MAIN)
    run(LATEXMK_BASE + [f"-jobname={MAIN}", f"{MAIN}.tex"], latex=True)


def target_production() -> None:
    """Run all Python scripts, then build the production PDF."""
    py_sources, src_sources = collect_sources()
    for src in py_sources + src_sources:
        execute_script(src)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    clean_stale_fdb(PRODUCTION_NAME)
    pdflatex_cmd = r'pdflatex %O "\def\draft{0}\input{%S}"'
    run(LATEXMK_BASE + [
        f"-jobname={PRODUCTION_NAME}",
        f"-pdflatex={pdflatex_cmd}",
        f"{MAIN}.tex",
    ], latex=True)


def target_clean() -> None:
    """Remove auxiliary LaTeX files and stamps."""
    run(["latexmk", "-c"], check=False, latex=True)

    aux_globs = ["*.out", "*.toc", "*.fls", "*.log",
                 "*.fdb_latexmk", "*.aux", "*.synctex.gz"]
    for pattern in aux_globs:
        for f in glob.glob(pattern):
            print(f"  Removing {f}")
            os.remove(f)

    if STAMP_DIR.exists():
        print(f"  Removing {STAMP_DIR}/")
        shutil.rmtree(STAMP_DIR)


def target_cleanall() -> None:
    """Remove everything including final PDFs."""
    target_clean()
    run(["latexmk", "-C"], check=False, latex=True)

    for pdf in [f"{MAIN}.pdf", f"{DRAFT_NAME}.pdf", f"{PRODUCTION_NAME}.pdf"]:
        if os.path.exists(pdf):
            print(f"  Removing {pdf}")
            os.remove(pdf)


# ── Entry point ────────────────────────────────────────────────────────────────

TARGETS = {
    "all":        target_py,
    "py":         target_py,
    "build":      target_build,
    "production": target_production,
    "clean":      target_clean,
    "cleanall":   target_cleanall,
}


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "target",
        nargs="?",
        default="all",
        choices=list(TARGETS),
        help="Build target (default: all)",
    )
    args = parser.parse_args()

    print(f"── build.py  target={args.target} ──")
    TARGETS[args.target]()
    print("── done ──")


if __name__ == "__main__":
    main()