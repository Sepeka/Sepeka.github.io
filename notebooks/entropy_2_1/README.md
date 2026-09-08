# Interactivate Information Theory — Section 2.1

A local marimo lesson based on Cover & Thomas, *Elements of Information Theory*,
second edition, Section 2.1 (pp. 13–16).

## Textbook fidelity

The textbook examples are the primary activities and should remain the default
in this and future notebooks. Preserve their labels, probabilities, assumptions,
and results. Added simulations and alternative strategies are optional extensions.

- Example 2.1.1: the coin represents the book's binary variable (heads is 1,
  tails is 0). Its draggable point and probability inputs explore the same
  binary entropy curve.
- Example 2.1.2: a, b, c, d have probabilities 50%, 25%, 12.5%, 12.5%.
  The default tree asks about a, then b, then c as needed, with an expected
  1.75 questions and entropy of 1.75 bits, as in the book.
- Random samples, alternative trees, and the free-weight playground extend
  these examples; they are not additional examples attributed to the book.

## Open the lesson

```bash
conda activate xrag
cd /home/sepeka/my_web_page/entropy_lab
python start.py
```

To open the reader-facing app without the code editor:

```bash
python -m marimo run entropy_2_1.py
```

Python requirements: marimo 0.24.0, numpy, matplotlib, and Pygments.
`lab_support.py`, `proof_help.py`, and `presentation.py` must stay beside the
notebook, with the `proofs` directory.
Also keep `entropy_explorer.html` and `scientific.py` beside the notebook. The
orange point can be dragged, clicked, or moved with arrow keys. Its probability
box, editable `prob = ...` assignment, and the probability box above the table
stay synchronized, updating the plot and all calculations.
The diagram previews entropy during dragging and commits the new probability
to Python on release. The visible function is the actual scientific core used
by the notebook's bit-entropy calculations. Viewer mode supports editing the
probability assignment; editing the full function remains available in Edit mode.

The editor shows the Python code that creates the plots. `marimo run` is the
reader-only view and hides the code. The **Light / Dark** appearance control
at the top opens the same notebook with marimo's native theme URL setting;
switching appearance reloads the page. Every plot includes a matching palette
for each theme, so the curves, axes, and labels remain readable.

The recommended `start.py` launcher starts an automatic viewer on
`http://localhost:2718` and a separate code editor on `http://localhost:2720`.
The viewer executes the notebook server-side for each new session, avoiding
the editor's empty-session reconnect behavior. The launcher explicitly enables
startup execution in the editor too. After restarting, refresh open browser tabs.
The first guessing round is shown as a worked example; **Draw a new secret**
starts a hidden round. Each claim includes its mathematical statement, followed by Lean code with
hover explanations and the recorded Lean result (distinct from a fresh check).
The prominent **Viewer mode / Edit mode** buttons link the two local servers
while preserving the theme. Use `start.py` to make both modes available.
They use separate Python sessions: saved code is shared, but transient slider
and game state is not shared between viewer and editor. The same buttons use
marimo's presentation/edit URL settings outside these designated local ports.

## Contents

- Draggable entropy curve, probability entry/code assignment, and repeatable random samples.
- Per-outcome logarithmic terms, entropy contributions, and bits/nats conversion.
- Four-symbol guessing game, three question trees, exact expectations,
  and simulated averages. Changing strategy or drawing a new secret resets
  the answer-reveal button.
- Probability-weight playground, renaming, and an impossible outcome.
- Mathematical statements of the two numbered lemmas, annotated Lean source,
  saved verification provenance, and a button for a fresh local Lean check.
- Hover over proof lines for explanations of the assumptions and tactics.
  Keyboard focus shows the same help; click or tap a line to pin its help open.
  The complete source includes the same notes. These authored explanations
  accompany the checked source; they are not a live Lean language-server view.
- An **Open and edit this proof in Lean Web** link that opens the complete
  proof source in the hosted MathlibDemo editor in a new tab. Readers need
  no local Lean installation. Lean Web uses its own Lean/mathlib version;
  its feedback is separate from this notebook's recorded local check.

## Formal scope

`proofs/Entropy.lean` proves nonnegative entropy and logarithm-base conversion
for **finite alphabets**. It also proves the zero contribution convention and
that normalization plus nonnegativity bounds each probability above by one.
The bases are greater than one. There are no unfinished proof placeholders.

The plots, Python implementation, infinite-alphabet case, concavity, maximum
entropy, and optimality of the example's question tree are not formally
certified by this file. The question-count example is numerically checked.
The prose explains the relationship between the formal statements and the book.

`lab_support.py` invokes Lean and audits the output of `#print axioms` for every
named theorem. Only `propext`, `Classical.choice`, and `Quot.sound` are allowed.
The UI never claims a fresh check based only on saved results. Saved results
are matched against the proof file's SHA-256, and include the mathlib revision,
Lean version, command, and output. They are a reproducibility record, not a
cryptographic attestation of the whole dependency tree.

## Lean configuration

The default uses the existing project and toolchains on this machine:

- Project: `/media/sepeka/New Volume/lean/book`
- Elan home: `/media/sepeka/New Volume/.elan`
- Toolchain: read from that project's `lean-toolchain` (v4.30.0).

Override with `ENTROPY_LEAN_PROJECT` and `ENTROPY_ELAN_HOME` if needed. Use a
project with the matching mathlib version and its compiled dependencies ready.
The notebook runs only its fixed proof source, with a timeout; it does not
execute arbitrary reader-submitted Lean.

To validate the proofs and update the saved result:

```bash
python lab_support.py
```

## Open in Molab

The notebook is stored in the website repository and can be imported directly
by Molab:

<https://molab.marimo.io/github/Sepeka/Sepeka.github.io/blob/main/notebooks/entropy_2_1/entropy_2_1.py>

Molab receives the surrounding repository files used by the notebook, including
the interactive entropy explorer, styles, Python helpers, and proof artifacts.
After creating a permanent Molab mirror, its share URL can replace the import
URL in the blog post.

The native Lean subprocess button requires Lean on the machine running the
notebook. Readers without Lean can use **Open and edit this proof in Lean Web**,
which provides live online proof checking, while the saved verification remains
visible in the notebook.
