# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "matplotlib>=3.9",
#     "numpy>=2.0",
#     "pygments>=2.19",
# ]
# ///

import marimo

__generated_with = "0.24.0"
app = marimo.App(
    width="medium",
    app_title="Interactivate Information Theory · Entropy",
    css_file="notebook.css",
)


@app.cell
def _():
    import marimo as mo
    import math
    import matplotlib.pyplot as plt
    import numpy as np
    import importlib
    from pathlib import Path
    import sys

    browser_runtime = sys.platform == "emscripten"
    if browser_runtime:
        from pyodide.http import open_url

        _directory = Path("/tmp/entropy-lab-support")
        _files = [
            "lab_support.py",
            "presentation.py",
            "proof_help.py",
            "scientific.py",
            "proofs/Entropy.lean",
            "proofs/verification.json",
        ]
        for _relative_path in _files:
            _destination = _directory / _relative_path
            _destination.parent.mkdir(parents=True, exist_ok=True)
            _source_url = mo.notebook_location() / "public" / _relative_path
            _destination.write_text(open_url(str(_source_url)).read())
    else:
        _directory = Path(__file__).resolve().parent
    if str(_directory) not in sys.path:
        sys.path.insert(0, str(_directory))
    _lab_support_module = importlib.import_module("lab_support")
    _proof_help_module = importlib.import_module("proof_help")
    _presentation_module = importlib.import_module("presentation")
    lab = _lab_support_module
    annotated_proof = _proof_help_module.annotated_proof
    binary_entropy_svg = _presentation_module.binary_entropy_svg
    figure_html = _presentation_module.figure_html
    scientific_code_html = _presentation_module.scientific_code_html
    navigation_control = _presentation_module.navigation_control

    return (
        annotated_proof,
        binary_entropy_svg,
        browser_runtime,
        figure_html,
        lab,
        math,
        mo,
        navigation_control,
        np,
        plt,
        scientific_code_html,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    # Information Theory
    ### 01 / Entropy

    Based on Section 2.1 of Cover & Thomas, *Elements of Information Theory*,
    second edition, pp. 13–16. Explanations and experiments here are original.
    """)
    return


@app.cell
def _(mo):
    navigation_params = mo.query_params()
    return (navigation_params,)


@app.cell
def _(browser_runtime, mo, navigation_control, navigation_params):
    _params = navigation_params.to_dict()
    _location = str(mo.notebook_location() or "")
    _in_browser_editor = browser_runtime and _location.rstrip("/").endswith("/edit")
    mo.Html(
        navigation_control(
            _params,
            browser_runtime,
            _in_browser_editor,
            _location,
        )
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Definition · Entropy

    Let X be a discrete random variable with alphabet 𝒳 and probability mass
    function p(x). Its entropy is

    \[
    H(X)=-\sum_{x\in\mathcal{X}}p(x)\log p(x).
    \]

    Logarithms are base 2 unless stated otherwise, so entropy
    is measured in bits. We use the convention that a zero-probability outcome
    contributes zero.

    Equivalently, apply the negative logarithm to each outcome's probability,
    multiply by that probability, and add the resulting terms.

    \[
    H(X)=\sum_{x\in\mathcal{X}}p(x)\bigl[-\log p(x)\bigr].
    \]
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## 1 · Example 2.1.1: Binary entropy

    In Example 2.1.1, the binary random variable is 1 with probability p and 0
    with probability 1 − p. Here, heads represents 1 and tails represents 0.
    Enter p in the probability box and observe how the entropy changes.
    """)
    return


@app.cell
def _(mo):
    coin_p = mo.ui.number(0, 1, step=0.01, value=0.5,
                          label="Probability of heads")
    toss_count = mo.ui.number(start=1, step=1, value=20, label="Number of tosses")
    toss_again = mo.ui.button(value=0, on_click=lambda n: n + 1, label="Toss again")
    coin_p
    return coin_p, toss_again, toss_count


@app.cell
def _(binary_entropy_svg, coin_p, mo):
    mo.Html(binary_entropy_svg(coin_p.value))
    return


@app.cell
def _(coin_p, mo, scientific_code_html):
    mo.Html(scientific_code_html(coin_p.value))
    return


@app.cell
def _(mo, toss_again, toss_count):
    mo.vstack([
        mo.md("""
        ### Coin-toss experiment

        Use the probability selected above to simulate independent coin tosses.
        On every toss, the coin lands heads with probability p and tails with
        probability 1 − p. Enter how many tosses to simulate, then click
        **Toss again** to generate a new random sample.
        """),
        toss_count,
        toss_again,
    ])
    return


@app.cell
def _(coin_p, figure_html, lab, mo, np, plt, toss_again, toss_count):
    _p = coin_p.value
    _tosses = lab.coin_tosses(_p, toss_count.value, 2100 + toss_again.value)
    _observed = sum(_tosses) / len(_tosses)
    _theory = lab.entropy([_p, 1 - _p])
    _empirical = lab.entropy([_observed, 1 - _observed])
    _sample_fig, _sample_ax = plt.subplots(figsize=(8, 3.6), layout="constrained")
    _sample_sizes = np.arange(1, len(_tosses) + 1)
    _running_heads = np.cumsum(_tosses) / _sample_sizes
    _running_entropy = [lab.entropy([float(x), float(1 - x)]) for x in _running_heads]
    _sample_ax.plot(_sample_sizes, _running_entropy, color="#219e93", lw=1.8, label="Entropy estimated from observed frequencies")
    _sample_ax.axhline(_theory, color="#de704b", ls="--", lw=1.5, label="Entropy of the chosen probability distribution")
    _sample_ax.set(xlabel="Number of tosses observed", ylabel="Estimated entropy (bits)",
                   title="Optional extension: estimating distribution entropy", ylim=(-0.03, 1.1))
    _sample_ax.spines[["top", "right"]].set_visible(False)
    _sample_ax.grid(alpha=0.15)
    _sample_ax.legend(frameon=False, fontsize=9, loc="lower right")
    _tiles = " ".join("🟣" if head else "🟠" for head in _tosses[:400])
    _insight = ("The outcome is certain. There is no uncertainty to resolve." if _p in (0, 1)
                else "A fair coin has the greatest binary uncertainty." if _p == 0.5
                else "A biased coin is more predictable. Try the complementary probability (1-p): the entropy stays the same.")
    _display = mo.vstack([
        mo.stat(f"{sum(_tosses)} / {len(_tosses)}", label="Heads observed in this sample"),
        mo.md(f"**Sample {toss_again.value + 1}.** The circles below show the simulated outcomes. Click **Toss again** to generate another sample using the same probability."),
        mo.md(f"**{'Tosses' if len(_tosses) < 400 else 'First 400 tosses'}** · 🟣 heads / 🟠 tails\n\n{_tiles}"),
        mo.callout(_insight, kind="info"),
        mo.vstack([
            mo.md("### Estimate entropy from observed frequencies"),
            mo.md("This estimation experiment is an addition to the notebook, not an example in Section 2.1. We use the observed fractions of heads and tails as an estimated probability distribution, then calculate that distribution’s entropy. This is an estimate of the coin distribution’s entropy, not an additional entropy belonging to the observations."),
            mo.stat(f"{_empirical:.4f}", label="Entropy estimated from observed frequencies · bits"),
            mo.Html(figure_html(_sample_fig, "Running estimate of distribution entropy from observed heads and tails frequencies")),
            mo.md("Click **Toss again** to update the estimate with a fresh sample. Estimates can fluctuate and need not equal the entropy calculated from the chosen heads probability."),
        ]),
    ])
    plt.close(_sample_fig)
    _display
    return


@app.cell
def _(mo):
    _intro = mo.md(r"""
    ## 2 · Reading the entropy sum

    For each outcome, the table shows p(x), the negative logarithm of p(x), and
    their product. Adding the products in the last column gives the entropy.
    Change the heads probability above and compare the two rows.
    """)
    table_p = mo.ui.number(0, 1, step=0.01, value=0.5,
                           label="Probability of heads")
    units = mo.ui.radio(["Bits (base 2)", "Nats (base e)"], value="Bits (base 2)", inline=True, label="Information units")
    mo.vstack([_intro, table_p, units])
    return table_p, units


@app.cell
def _(figure_html, lab, math, mo, plt, table_p, units):
    _base = 2 if units.value.startswith("Bits") else math.e
    _unit = "bits" if _base == 2 else "nats"
    _log_term_label = "−log₂ p(x)" if _base == 2 else "−ln p(x)"
    _probability = table_p.value
    _p = [_probability, 1 - _probability]
    _rows = []
    for _name, _prob, _contribution in zip(["Heads", "Tails"], _p, lab.contributions(_p, _base)):
        _log_term = f"{-math.log(_prob, _base):.4f} {_unit}" if _prob else "Unbounded (impossible event)"
        _rows.append({
            "name": _name,
            "probability": f"{_prob:.2f}",
            "log_term": _log_term,
            "contribution": f"{_contribution:.4f} {_unit}",
        })
    _table_rows = "".join(
        f"<tr><td>{row['name']}</td><td>{row['probability']}</td>"
        f"<td>{row['log_term']}</td><td>{row['contribution']}</td></tr>"
        for row in _rows
    )
    _table = mo.Html(f"""
    <div class="entropy-breakdown-table">
      <table>
        <thead><tr>
          <th>Outcome</th>
          <th>Probability <span class="entropy-table-formula">p(x)</span></th>
          <th><span class="entropy-table-formula">{_log_term_label}</span></th>
          <th>Contribution <span class="entropy-table-formula">p(x) × [{_log_term_label}]</span></th>
        </tr></thead>
        <tbody>{_table_rows}</tbody>
      </table>
    </div>
    """)
    _fig, _ax = plt.subplots(figsize=(8, 2.5), layout="constrained")
    _ax.barh(["Heads", "Tails"], lab.contributions(_p, _base), color=["#6554c0", "#de704b"])
    _ax.set(title=f"Contribution = p(x) × [{_log_term_label}]",
            xlabel=f"Contribution to entropy ({_unit})", xlim=(0, 0.6))
    _ax.spines[["top", "right"]].set_visible(False)
    _display = mo.vstack([
        _table, mo.Html(figure_html(_fig, "Weighted contributions of heads and tails to entropy")),
        mo.md(f"**Entropy (the sum of the two contributions): {lab.entropy(_p, _base):.4f} {_unit}.** For a rare outcome, the negative logarithm is large while p(x) is small."),
    ])
    plt.close(_fig)
    _display
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## 3 · Find the hidden symbol
    ### Example 2.1.2 · Some questions are more useful than others

    A secret is drawn from **a: 50%, b: 25%, c: 12.5%, d: 12.5%**.
    Choose a strategy, then reveal its yes/no answers one at a time. Each tree
    identifies every possible symbol. Which uses the fewest questions **on average**?
    """)
    return


@app.cell
def _(browser_runtime, lab, mo):
    strategy = mo.ui.radio(list(lab.TREES), value="Book's strategy", label="Question strategy")
    new_secret = mo.ui.button(value=0, on_click=lambda n: n + 1, label="Draw a new secret")
    mo.hstack([strategy, new_secret])
    return new_secret, strategy


@app.cell
def _(mo, new_secret, strategy):
    _round_identity = (new_secret.value, strategy.value)
    reveal_answer = mo.ui.button(value=3 if new_secret.value == 0 else 0, on_click=lambda n: n + 1, label="Reveal next answer")
    reveal_answer
    return (reveal_answer,)


@app.cell
def _(lab, mo, new_secret, reveal_answer, strategy):
    _secret = lab.draw_symbol(400 + new_secret.value)
    _path = lab.question_path(lab.TREES[strategy.value], _secret)
    _visible = _path[:reveal_answer.value]
    _lines = [f"{i + 1}. {q} **{'Yes' if a else 'No'}**" for i, (q, a) in enumerate(_visible)]
    _done = reveal_answer.value >= len(_path)
    _status = f"**Found: {_secret}.** This round took {len(_path)} questions." if _done else "The symbol is still hidden. Reveal another answer."
    mo.vstack([mo.md("\n".join(_lines) if _lines else "No questions asked yet."), mo.callout(mo.md(_status), kind="success" if _done else "info")])
    return


@app.cell
def _(figure_html, lab, mo, plt, strategy):
    _tree = lab.TREES[strategy.value]
    _codes = lab.codewords(_tree)
    _fig, _ax = plt.subplots(figsize=(8, 3.5), layout="constrained")
    def _draw(node, x, y, spread):
        if isinstance(node, str):
            _ax.text(x, y, node, ha="center", va="center", fontsize=13,
                     bbox=dict(boxstyle="round,pad=.4", fc="#ece8ff", ec="#6554c0"))
        else:
            _label = "in {" + ", ".join(lab.leaves(node[0])) + "}?"
            _ax.text(x, y, _label, ha="center", va="center", fontsize=10,
                     bbox=dict(boxstyle="round,pad=.3", fc="#fff4df", ec="#c99b4b"))
            for _child, _dx, _edge in [(node[0], -spread, "yes / 0"), (node[1], spread, "no / 1")]:
                _ax.plot([x, x + _dx], [y - 0.07, y - 0.9], color="#aaa", zorder=0)
                _ax.text(x + _dx * .6, y - .48, _edge, ha="center", fontsize=8)
                _draw(_child, x + _dx, y - 1, spread * .48)
    _draw(_tree, 0, 0, 1.5)
    _ax.set(xlim=(-3, 3), ylim=(-3.5, .5))
    _ax.axis("off")
    _rows = [{"Symbol": s, "Probability": p, "Code (yes=0, no=1)": _codes[s], "Questions": len(_codes[s])}
             for s, p in zip(lab.SYMBOLS, lab.BOOK_P)]
    _comparison = "\n".join(f"- {name}: **{lab.expected_questions(tree):.3f} questions** on average." for name, tree in lab.TREES.items())
    _display = mo.vstack([mo.Html(figure_html(_fig, "Binary question tree for the selected strategy")), mo.ui.table(_rows, selection=None), mo.md(_comparison),
               mo.callout("The source entropy is 1.75 bits. The book's tree attains 1.75 questions on average. This exact equality is possible for these probabilities; other distributions need not attain it with single-symbol binary trees.", kind="info")])
    plt.close(_fig)
    _display
    return


@app.cell
def _(mo):
    repeat_games = mo.ui.button(value=0, on_click=lambda n: n + 1, label="Simulate 1,000 more rounds (fresh sample)")
    repeat_games
    return (repeat_games,)


@app.cell
def _(lab, mo, repeat_games, strategy):
    _symbols = [lab.draw_symbol(9000 + repeat_games.value * 1000 + i) for i in range(1000)]
    _mean = sum(len(lab.question_path(lab.TREES[strategy.value], s)) for s in _symbols) / len(_symbols)
    mo.md(f"**Simulation:** {_mean:.3f} questions per symbol over 1,000 independent rounds. **Exact expectation:** {lab.expected_questions(lab.TREES[strategy.value]):.3f}. The sample average fluctuates; the expectation does not.")
    return


@app.cell
def _(mo):
    _intro = mo.md("""
    ## 4 · Build your own source

    Set four weights; we divide each by their total to obtain valid probabilities.
    Try equal weights, then put all the weight on one outcome. Rename the
    outcomes and add an impossible outcome: do either change the entropy?
    """)
    weights = mo.ui.array([mo.ui.slider(0, 16, value=v, step=1, show_value=True, full_width=True, label=f"Weight {i + 1}") for i, v in enumerate([4, 2, 1, 1])])
    rename = mo.ui.radio(["Letters", "Weather"], value="Letters", inline=True, label="Outcome labels")
    add_zero = mo.ui.checkbox(label="Add a fifth outcome with zero probability")
    mo.vstack([_intro, weights, mo.hstack([rename, add_zero])])
    return add_zero, rename, weights


@app.cell
def _(add_zero, figure_html, lab, mo, plt, rename, weights):
    mo.stop(sum(weights.value) == 0, mo.callout("At least one weight must be positive. All-zero weights do not define a probability distribution.", kind="warn"))
    playground_p = lab.probabilities(weights.value)
    _names = ["a", "b", "c", "d"] if rename.value == "Letters" else ["Sun", "Rain", "Cloud", "Snow"]
    if add_zero.value:
        playground_p = playground_p + [0.0]
        _names.append("Impossible")
    _fig, _axes = plt.subplots(1, 2, figsize=(8, 3), layout="constrained")
    _axes[0].bar(_names, playground_p, color="#6554c0")
    _axes[0].set(title="Probabilities", ylim=(0, 1))
    _axes[1].bar(_names, lab.contributions(playground_p), color="#de704b")
    _axes[1].set(title="Contributions to entropy · bits", ylim=(0, .6))
    for _ax in _axes:
        _ax.spines[["top", "right"]].set_visible(False)
        _ax.tick_params(axis="x", labelsize=8)
    _display = mo.vstack([mo.Html(figure_html(_fig, "Outcome probabilities and their entropy contributions")), mo.stat(f"{lab.entropy(playground_p):.4f} bits", label="Entropy from the chosen probabilities"),
        mo.accordion({"What to discover": mo.md("""
        - Equal probabilities on the four adjustable outcomes give **2 bits**.
        - A certain outcome gives **0 bits**.
        - Renaming outcomes changes no probabilities and therefore no entropy.
        - A zero-probability outcome adds no contribution. The fifth outcome
          remains fixed at zero, so this playground's maximum remains 2 bits.
        """)})])
    plt.close(_fig)
    _display
    return


@app.cell
def _(mo):
    _intro = mo.md("""
    ## 5 · From experiments to proofs

    The plots show particular cases. A proof covers **every distribution in its
    stated domain**. Here we formalize the two numbered lemmas of Section 2.1
    for finite alphabets, including outcomes with zero probability.

    The displayed proofs were checked offline with Lean. Hover over the proof
    lines for help. The Python visualizations themselves are not formally verified.
    """)
    theorem_choice = mo.ui.radio(["2.1.1 · Nonnegativity", "2.1.2 · Change of base"], value="2.1.1 · Nonnegativity", inline=True)
    mo.vstack([_intro, theorem_choice])
    return (theorem_choice,)


@app.cell
def _(annotated_proof, lab, mo, theorem_choice):
    _source = lab.PROOF.read_text()
    if theorem_choice.value.startswith("2.1.1"):
        _statement = r"""
        **Claim:** entropy is nonnegative for every finite probability distribution and every base greater than one.

        \[
        H_b(X) = -\sum_{x\in\mathcal{X}}p(x)\log_b p(x) \ge 0,
        \qquad b>1.
        \]
        """
    else:
        _statement = r"""
        **Claim:** changing the logarithm base scales entropy by a constant conversion factor.

        \[
        H_b(X) = (\log_b a)\,H_a(X), \qquad a>1,\ b>1.
        \]
        """
    _selected = {"entropy_nonnegative", "distribution_entropy_nonnegative"} if theorem_choice.value.startswith("2.1.1") else {"entropy_change_base"}
    mo.vstack([mo.md(_statement),
        mo.md("**Explore the Lean proof.** Hover over a code line to see what it does. Click or tap to keep its explanation open; keyboard users can focus a line with Tab."),
        mo.Html(annotated_proof(_source, selected=_selected, view_id="selected")),
        mo.accordion({"Read the complete Lean source": mo.Html(annotated_proof(_source)),
                      "Scope and foundations": mo.md("""
        **Finite alphabets only.** Countably infinite alphabets and possibly infinite
        entropies are outside these formal statements. Both bases are above one.
        Exact optimality of the guessing tree, the entropy curve's concavity,
        and its maximum are illustrated here but are not certified by this proof file.

        The checker audits each named theorem's dependencies. Standard Lean/mathlib
        foundations (`propext`, `Classical.choice`, `Quot.sound`) are allowed;
        `sorryAx` and additional assumptions introduced as axioms are not.
        """)})])
    return


@app.cell
def _(lab, mo):
    from urllib.parse import quote

    _lean_web_url = "https://live.lean-lang.org/#project=MathlibDemo&code=" + quote(lab.PROOF.read_text(), safe="")
    mo.vstack([
        mo.Html(
            f'<a href="{_lean_web_url}" target="_blank" rel="noopener noreferrer" '
            'style="display:inline-block;padding:10px 16px;border-radius:6px;'
            'background:#6554c0;color:white;text-decoration:none;font-weight:600;">'
            'Open and edit this proof in Lean Web</a>'
        ),
        mo.md("Opens both proofs and their supporting definitions in a new tab. You can edit them and inspect Lean’s feedback without installing Lean. Lean Web checks the code on its server; its Lean/mathlib version may differ from the locally verified version."),
    ])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ---
    **Takeaway.** Entropy measures average uncertainty in a distribution. A
    predictable source has less to tell us; a good sequence of questions uses
    that predictability. The experiments build intuition, and the two Lean
    proofs establish nonnegativity and unit conversion under explicit assumptions.
    """)
    return


if __name__ == "__main__":
    app.run()
