import Mathlib.Analysis.SpecialFunctions.Log.Base
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring

/-!
Section 2.1 of Cover and Thomas, Elements of Information Theory (2nd ed.).
These are proofs for FINITE alphabets. Real.logb is totalized in mathlib;
the zero-probability contribution is zero, as in the textbook convention.
-/
namespace EntropyLab

/-- Entropy in a logarithm base b, for finitely many outcome weights. -/
noncomputable def entropy {n : ℕ} (b : ℝ) (p : Fin n → ℝ) : ℝ :=
  ∑ i, -(p i) * Real.logb b (p i)

/-- The convention for an impossible outcome is satisfied exactly. -/
theorem zero_contribution (b : ℝ) : -(0 : ℝ) * Real.logb b 0 = 0 := by
  simp

/-- Lemma 2.1.1: every contribution, hence their sum, is nonnegative.
Normalization is unnecessary for this stronger termwise statement. -/
theorem entropy_nonnegative {n : ℕ} (b : ℝ) (p : Fin n → ℝ)
    (hb : 1 < b) (hp0 : ∀ i, 0 ≤ p i) (hp1 : ∀ i, p i ≤ 1) :
    0 ≤ entropy b p := by
  unfold entropy
  apply Finset.sum_nonneg
  intro i _
  have hlog : Real.logb b (p i) ≤ 0 := Real.logb_nonpos hb (hp0 i) (hp1 i)
  exact mul_nonneg_of_nonpos_of_nonpos (neg_nonpos.mpr (hp0 i)) hlog

/-- A normalized finite probability distribution has each probability at most one. -/
theorem probability_le_one {n : ℕ} (p : Fin n → ℝ)
    (hp0 : ∀ i, 0 ≤ p i) (hsum : ∑ i, p i = 1) (i : Fin n) : p i ≤ 1 := by
  calc
    p i ≤ ∑ j, p j := Finset.single_le_sum (fun j _ => hp0 j) (Finset.mem_univ i)
    _ = 1 := hsum

/-- Lemma 2.1.1 stated directly for normalized finite distributions. -/
theorem distribution_entropy_nonnegative {n : ℕ} (b : ℝ) (p : Fin n → ℝ)
    (hb : 1 < b) (hp0 : ∀ i, 0 ≤ p i) (hsum : ∑ i, p i = 1) :
    0 ≤ entropy b p := by
  exact entropy_nonnegative b p hb hp0 (probability_le_one p hp0 hsum)

/-- Lemma 2.1.2: changing units multiplies the whole entropy by one factor.
Both bases are above one, the usual setting for information units. -/
theorem entropy_change_base {n : ℕ} (a b : ℝ) (p : Fin n → ℝ)
    (ha : 1 < a) (_hb : 1 < b) :
    entropy b p = Real.logb b a * entropy a p := by
  unfold entropy
  rw [Finset.mul_sum]
  apply Finset.sum_congr rfl
  intro i _
  have hchange : Real.logb b a * Real.logb a (p i) = Real.logb b (p i) :=
    Real.mul_logb (by linarith) (by linarith) (by linarith)
  rw [← hchange]
  ring

end EntropyLab

-- The checker wrapper audits these outputs, allowing only standard foundations.
#print axioms EntropyLab.zero_contribution
#print axioms EntropyLab.entropy_nonnegative
#print axioms EntropyLab.probability_le_one
#print axioms EntropyLab.distribution_entropy_nonnegative
#print axioms EntropyLab.entropy_change_base
