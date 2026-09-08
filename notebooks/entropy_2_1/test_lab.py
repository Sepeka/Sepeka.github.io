"""Check numerical identities, edge cases, and decision-tree behavior."""
import math
import unittest
from lab_support import (BOOK_P, SYMBOLS, TREES, codewords, contributions,
                         entropy, expected_questions, probabilities, question_path)


class EntropyTests(unittest.TestCase):
    def test_book_values(self):
        self.assertEqual(entropy([1, 0]), 0)
        self.assertEqual(entropy([0.5, 0.5]), 1)
        self.assertEqual(entropy(BOOK_P), 1.75)
        self.assertEqual(entropy([0.25] * 4), 2)

    def test_boundaries_and_units(self):
        for k in range(101):
            p = [k / 100, 1 - k / 100]
            self.assertGreaterEqual(entropy(p), 0)
            self.assertLessEqual(entropy(p), 1)
            self.assertAlmostEqual(entropy(p), entropy(p[::-1]))
            self.assertAlmostEqual(entropy(p, math.e), entropy(p) * math.log(2))
            self.assertAlmostEqual(sum(contributions(p)), entropy(p))
        self.assertEqual(entropy(BOOK_P), entropy([*BOOK_P, 0]))

    def test_invalid_weights(self):
        for weights in [[0, 0], [-1, 2], [math.nan, 1], [math.inf, 1]]:
            with self.assertRaises(ValueError):
                probabilities(weights)
        self.assertEqual(probabilities([4, 2, 1, 1]), list(BOOK_P))

    def test_question_trees(self):
        self.assertEqual(expected_questions(TREES["Book's strategy"]), 1.75)
        self.assertEqual(expected_questions(TREES["Always two questions"]), 2)
        self.assertEqual(expected_questions(TREES["Rare outcome first"]), 2.625)
        for tree in TREES.values():
            codes = codewords(tree)
            self.assertEqual(set(codes), set(SYMBOLS))
            for a in SYMBOLS:
                self.assertEqual(len(codes[a]), len(question_path(tree, a)))
                for b in SYMBOLS:
                    if a != b:
                        self.assertFalse(codes[b].startswith(codes[a]))


if __name__ == '__main__':
    unittest.main()
