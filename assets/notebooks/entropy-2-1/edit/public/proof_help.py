"""An annotated view of the exact Lean source; no change to the checked proofs."""
from html import escape
import re


THEOREMS = {
    'entropy_nonnegative': 'Nonnegativity, one contribution at a time',
    'distribution_entropy_nonnegative': 'Nonnegativity for a probability distribution',
    'probability_le_one': 'Why each probability is at most one',
    'entropy_change_base': 'Changing the unit of information',
    'zero_contribution': 'An impossible outcome contributes zero',
}


def line_help(line, declaration):
    text = line.strip()
    if text.startswith('import '):
        module = text.removeprefix('import ')
        return {
            'Mathlib.Analysis.SpecialFunctions.Log.Base': 'Load mathlib’s real logarithm in an arbitrary base and the sign and conversion lemmas used below.',
            'Mathlib.Tactic.Linarith': 'Load linarith, which derives linear inequalities from the hypotheses. Here it shows that a base greater than one is neither zero, one, nor minus one.',
            'Mathlib.Tactic.Ring': 'Load ring, which proves polynomial identities by normalizing expressions. Here it rearranges products after the logarithm conversion has been proved.',
        }.get(module, 'Import this Lean module and its declarations.')
    if text.startswith('namespace '):
        return 'Place our definitions and theorems in the EntropyLab namespace, so their names do not conflict with library declarations.'
    if text.startswith('end '):
        return 'Close the EntropyLab namespace.'
    if text.startswith('#print axioms'):
        return 'Ask Lean to report the foundational axioms this theorem depends on. The notebook checks these reports and rejects unfinished proofs and additional axioms.'
    if text.startswith('noncomputable def entropy'):
        return 'Define entropy for a finite alphabet. Fin n indexes n outcomes; p assigns a real weight to each. Noncomputable permits the exact real logarithm in a mathematical definition; it does not leave a proof unfinished.'
    if text.startswith('∑ i,'):
        return 'Add the weighted information contribution of each outcome. Negating each probability before multiplying by its logarithm is the textbook entropy convention.'
    if text.startswith('theorem '):
        return {
            'zero_contribution': 'Claim that an outcome with zero probability contributes exactly zero, for every logarithm base.',
            'entropy_nonnegative': 'State the helper theorem: entropy is nonnegative whenever every weight is between zero and one and the logarithm base is greater than one.',
            'probability_le_one': 'State the normalization lemma. Nonnegative weights summing to one cannot contain a weight greater than one.',
            'distribution_entropy_nonnegative': 'State the textbook result for a normalized finite probability distribution.',
            'entropy_change_base': 'State the conversion theorem for two logarithm bases and the same finite collection of weights.',
        }.get(declaration, 'Introduce a theorem with the name, parameters, hypotheses, and conclusion shown here.')
    if text.startswith('(hb :'):
        return 'Name the assumptions: hb says the logarithm base exceeds one; hp0 says every weight is nonnegative. hp1 bounds each weight above by one, while hsum, when present, says their sum is one.'
    if text.startswith('(hp0 :'):
        return 'Assume every weight is nonnegative and the finite sum is one. The index i identifies the particular probability that we want to bound.'
    if text.startswith('(ha :'):
        return 'Both bases exceed one. The algebraic conversion actually needs only the restrictions on a here; _hb records the usual information-theory restriction on b without using it in the proof.'
    if text.startswith('0 ≤ entropy'):
        return 'This is the conclusion to establish: the entropy is nonnegative. The keyword by begins the sequence of proof tactics.'
    if text.startswith('entropy b p ='):
        return 'The desired conclusion says the entropy in base b is the entropy in base a multiplied by the base-conversion factor.'
    if text == 'simp':
        return 'Simplify the zero contribution using identities for negation and multiplication by zero. No limiting argument or numerical approximation is needed for this algebraic identity.'
    if text == 'unfold entropy':
        return 'Replace the name entropy with its definition as a finite sum. The goal now exposes the individual contributions.'
    if text == 'apply Finset.sum_nonneg':
        return 'Use the theorem that a finite sum is nonnegative if each summand is nonnegative. It remains to prove the sign of an arbitrary contribution.'
    if text == 'intro i _':
        return ('Choose an arbitrary outcome i. The underscore discards the unused fact that i belongs to the universal finite index set. Now compare the two contributions at i.'
                if declaration == 'entropy_change_base' else
                'Choose an arbitrary outcome i. The underscore discards the unused fact that i belongs to the universal finite index set. Now prove that this outcome’s contribution is nonnegative.')
    if text.startswith('have hlog'):
        return 'Establish a local fact named hlog. For a base above one and an argument between zero and one, mathlib’s totalized logarithm is nonpositive. The zero-weight entropy term agrees with the book’s convention.'
    if text.startswith('exact mul_nonneg_of_nonpos_of_nonpos'):
        return 'Finish the summand proof: the negative probability is nonpositive, and hlog says the logarithm is nonpositive. Multiplying these two nonpositive numbers gives a nonnegative contribution.'
    if text == 'calc':
        return 'Begin a calculation in which each line states a justified inequality or equality. Lean chains these steps to reach the target.'
    if text.startswith('p i ≤ ∑'):
        return 'A single weight is at most the sum of all weights because every other weight is nonnegative. The library lemma single_le_sum makes this reasoning explicit.'
    if text == '_ = 1 := hsum':
        return 'Replace the sum from the preceding line by one, using the normalization assumption hsum. This completes the upper bound on the chosen probability.'
    if text.startswith('exact entropy_nonnegative'):
        return 'Apply the termwise nonnegativity theorem. The probability_le_one lemma supplies its upper-bound assumption from normalization, so the result now applies to every finite probability distribution.'
    if text == 'rw [Finset.mul_sum]':
        return 'Distribute the conversion factor across the sum on the right. Both sides are now finite sums over the same outcome indices.'
    if text == 'apply Finset.sum_congr rfl':
        return 'To prove the sums equal, prove their corresponding summands equal. rfl confirms that both sums use exactly the same index set.'
    if text.startswith('have hchange'):
        return 'Introduce the logarithm change-of-base identity for this outcome as a local fact named hchange. This isolates the analytic fact from the algebra that follows.'
    if text.startswith('Real.mul_logb'):
        return 'Use mathlib’s logarithm conversion theorem. Each linarith call derives one required exclusion for base a: it is not zero, one, or minus one, because ha says it exceeds one.'
    if text == 'rw [← hchange]':
        return 'Rewrite the base-b logarithm using hchange in the reverse direction. Both sides now involve the same logarithm and the same conversion factor.'
    if text == 'ring':
        return 'Close the goal by rearranging multiplication. ring treats the logarithm values as real quantities and checks the remaining polynomial identity exactly.'
    return None


def annotated_proof(source, selected=None, view_id='full'):
    """Render source lines with authored hover notes; selected filters declarations."""
    declaration = None
    comment = False
    rows = []
    for number, line in enumerate(source.splitlines(), 1):
        text = line.strip()
        if comment or text.startswith('/-') or text.startswith('--') or not text:
            if text.startswith('/-'):
                comment = '-/' not in text
            if '-/' in text:
                comment = False
            if not selected:
                rows.append(f'<div class="entropy-lean-plain"><span class="entropy-lean-number" aria-hidden="true">{number}</span><code>{escape(line) or "&nbsp;"}</code></div>')
            continue
        match = re.match(r'(?:noncomputable def|theorem) (\w+)', text)
        if match:
            declaration = match.group(1)
        if selected and declaration not in selected:
            continue
        if selected and (text.startswith('end ') or text.startswith('#print')):
            continue
        help_text = line_help(line, declaration)
        # Unknown lines remain visible verbatim, without inventing an explanation.
        code = f'<span class="entropy-lean-number" aria-hidden="true">{number}</span><code>{escape(line)}</code>'
        if help_text:
            tip_id = f'lean-help-{view_id}-{number}'
            rows.append(f'<details class="entropy-lean-line" data-line="{number}"><summary aria-describedby="{tip_id}">{code}</summary>'
                        f'<div class="entropy-lean-help" id="{tip_id}" role="tooltip">{escape(help_text)}</div></details>')
        else:
            rows.append(f'<div class="entropy-lean-plain">{code}</div>')
    return '''<style>
    .entropy-lean {border:1px solid #b9b3d6;border-radius:8px;padding:12px 4px;background:var(--background,#fff);color:var(--foreground,#20202b);margin:12px 0;}
    .entropy-lean code {font-family:var(--monospace-font,monospace);font-size:13px;white-space:pre-wrap;overflow-wrap:anywhere;background:none;padding:0;color:inherit;}
    .entropy-lean-number {display:inline-block;flex:0 0 2.5em;text-align:right;margin-right:1em;opacity:.5;font:12px monospace;user-select:none;}
    .entropy-lean-line {position:relative;margin:0;border:none;padding:0;}
    .entropy-lean-line>summary,.entropy-lean-plain {display:flex;align-items:baseline;padding:4px 8px;line-height:1.65;list-style:none;border-radius:4px;}
    .entropy-lean-line>summary {cursor:help;}
    .entropy-lean-line>summary::-webkit-details-marker {display:none;}
    .entropy-lean-line:hover>summary,.entropy-lean-line:focus-within>summary {background:rgba(101,84,192,.12);}
    .entropy-lean-line>summary:focus-visible {outline:2px solid #6554c0;outline-offset:1px;}
    .entropy-lean-help {display:none;position:absolute;z-index:30;left:3em;top:100%;width:calc(100% - 4em);max-width:620px;box-sizing:border-box;white-space:normal;padding:12px 16px;border:1px solid #6554c0;border-radius:6px;background:#f5f2ff;color:#252039;box-shadow:0 4px 16px #0002;font:14px/1.6 system-ui,sans-serif;}
    .entropy-lean-line:hover>.entropy-lean-help,.entropy-lean-line:focus-within>.entropy-lean-help,.entropy-lean-line[open]>.entropy-lean-help {display:block;}
    .entropy-lean-line:hover::details-content,.entropy-lean-line:focus-within::details-content {content-visibility:visible;}
    .entropy-lean-line[open]>.entropy-lean-help {position:relative;top:auto;margin-bottom:8px;}
    .dark .entropy-lean {background:#191b23;color:#e6e8f2;}
    .dark .entropy-lean-help {background:#302c48;color:#f1edff;border-color:#a99aff;}
    :host-context(.dark) .entropy-lean {background:#191b23;color:#e6e8f2;}
    :host-context(.dark) .entropy-lean-help {background:#302c48;color:#f1edff;border-color:#a99aff;}
    </style><div class="entropy-lean" aria-label="Lean proof with step explanations">''' + ''.join(rows) + '</div>'
