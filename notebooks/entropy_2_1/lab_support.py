"""Numerical experiments and a real, auditable Lean checker for the notebook."""
from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path
import random
import re
import time
from scientific import entropy_bits

ROOT = Path(__file__).resolve().parent
PROOF = ROOT / "proofs" / "Entropy.lean"
DEFAULT_PROJECT = Path("/media/sepeka/New Volume/lean/book")
DEFAULT_ELAN = Path("/media/sepeka/New Volume/.elan")
PROVEN_THEOREMS = (
    "zero_contribution", "entropy_nonnegative", "probability_le_one",
    "distribution_entropy_nonnegative", "entropy_change_base",
)


def probabilities(weights):
    values = [float(w) for w in weights]
    if not values or any(not math.isfinite(w) or w < 0 for w in values):
        raise ValueError("Use finite, nonnegative weights.")
    total = sum(values)
    if total <= 0:
        raise ValueError("Give at least one outcome a positive weight.")
    return [w / total for w in values]


def entropy(p, base=2):
    if base <= 1 or not math.isfinite(base):
        raise ValueError("The logarithm base must be greater than one.")
    if any(x < 0 or not math.isfinite(x) for x in p) or not math.isclose(sum(p), 1):
        raise ValueError("Probabilities must be nonnegative and sum to one.")
    if base == 2:
        return entropy_bits(p)
    return max(0.0, -sum(x * math.log(x, base) for x in p if x > 0))


def contributions(p, base=2):
    return [max(0.0, -x * math.log(x, base)) if x > 0 else 0.0 for x in p]


def coin_tosses(p, count, seed):
    rng = random.Random(seed)
    return [rng.random() < p for _ in range(count)]


# Each question partitions the remaining possibilities; leaves are single symbols.
TREES = {
    "Book's strategy": ("a", ("b", ("c", "d"))),
    "Always two questions": (("a", "b"), ("c", "d")),
    "Rare outcome first": ("d", ("c", ("a", "b"))),
}
SYMBOLS = ("a", "b", "c", "d")
BOOK_P = (0.5, 0.25, 0.125, 0.125)


def leaves(tree):
    return [tree] if isinstance(tree, str) else leaves(tree[0]) + leaves(tree[1])


def question_path(tree, symbol):
    path = []
    while not isinstance(tree, str):
        group = leaves(tree[0])
        answer = symbol in group
        path.append(("Is the symbol in {" + ", ".join(group) + "}?", answer))
        tree = tree[0] if answer else tree[1]
    return path


def codewords(tree):
    return {s: "".join("0" if a else "1" for _, a in question_path(tree, s)) for s in SYMBOLS}


def expected_questions(tree, p=BOOK_P):
    return sum(prob * len(question_path(tree, s)) for s, prob in zip(SYMBOLS, p))


def draw_symbol(seed):
    return random.Random(seed).choices(SYMBOLS, weights=BOOK_P, k=1)[0]


def lean_config():
    project = Path(os.environ.get("ENTROPY_LEAN_PROJECT", DEFAULT_PROJECT))
    elan = Path(os.environ.get("ENTROPY_ELAN_HOME", DEFAULT_ELAN))
    toolchain = (project / "lean-toolchain").read_text().strip()
    bindir = elan / "toolchains" / toolchain.replace("/", "--").replace(":", "---") / "bin"
    env = os.environ.copy()
    env["PATH"] = str(bindir) + os.pathsep + env.get("PATH", "")
    env["ELAN_HOME"] = str(elan)
    return project, bindir, env, toolchain


def check_proofs():
    """Run Lean on the fixed local source, then audit actual theorem dependencies.

    No user-submitted Lean is executed. Nothing is reported as verified solely
    from the process exit code: every named theorem must have an axiom report.
    """
    import signal
    import subprocess

    started = time.time()
    result = {"ok": False, "sha256": hashlib.sha256(PROOF.read_bytes()).hexdigest(),
              "checked_at": time.strftime("%Y-%m-%d %H:%M:%S %Z"), "output": ""}
    try:
        project, bindir, env, toolchain = lean_config()
        result["toolchain"] = toolchain
        result["command"] = [str(bindir / "lake"), "env", "lean", str(PROOF)]
        version = subprocess.run([str(bindir / "lean"), "--version"], env=env,
                                 capture_output=True, text=True, timeout=15, check=True)
        result["lean_version"] = version.stdout.strip()
        mathlib = project / ".lake" / "packages" / "mathlib"
        revision = subprocess.run(["git", "-C", str(mathlib), "rev-parse", "HEAD"],
                                  capture_output=True, text=True, timeout=15, check=True)
        result["mathlib_revision"] = revision.stdout.strip()
        with subprocess.Popen(result["command"], cwd=project, env=env,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              text=True, start_new_session=True) as proc:
            try:
                stdout, stderr = proc.communicate(timeout=180)
            except subprocess.TimeoutExpired:
                # Lake may launch a Lean child: stop the entire check on timeout.
                os.killpg(proc.pid, signal.SIGKILL)
                stdout, stderr = proc.communicate()
                result["output"] = stdout + stderr
                raise
        result["output"] = stdout + stderr
        result["exit_code"] = proc.returncode
        allowed = {"propext", "Classical.choice", "Quot.sound"}
        audits = {}
        for theorem in PROVEN_THEOREMS:
            full = "EntropyLab." + theorem
            match = re.search(re.escape(full) + r"'? depends on axioms: \[([^\]]*)\]", result["output"], re.S)
            if match:
                axioms = {x.strip() for x in match.group(1).split(",") if x.strip()}
                audits[theorem] = sorted(axioms)
            elif re.search(re.escape(full) + r"'? does not depend on any axioms", result["output"]):
                audits[theorem] = []
        result["axioms"] = audits
        result["ok"] = (proc.returncode == 0 and len(audits) == len(PROVEN_THEOREMS)
                        and all(set(a) <= allowed for a in audits.values())
                        and "sorry" not in result["output"].lower()
                        and result["sha256"] == hashlib.sha256(PROOF.read_bytes()).hexdigest())
        if not result["ok"]:
            result["error"] = "Lean or the theorem dependency audit did not pass; inspect the log."
    except (OSError, subprocess.SubprocessError) as exc:
        result["error"] = str(exc)
    result["seconds"] = round(time.time() - started, 2)
    return result


def saved_verification():
    path = ROOT / "proofs" / "verification.json"
    if not path.exists():
        return None
    result = json.loads(path.read_text())
    result["source_matches"] = result.get("sha256") == hashlib.sha256(PROOF.read_bytes()).hexdigest()
    return result


if __name__ == "__main__":
    report = check_proofs()
    (ROOT / "proofs" / "verification.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    raise SystemExit(0 if report["ok"] else 1)
