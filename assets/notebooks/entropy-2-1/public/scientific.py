"""Scientific core shown to readers in the interactive lesson."""
import math


def entropy_bits(probabilities):
    """Entropy in bits for a valid finite probability distribution."""
    return sum(-p * math.log2(p) for p in probabilities if p > 0)
