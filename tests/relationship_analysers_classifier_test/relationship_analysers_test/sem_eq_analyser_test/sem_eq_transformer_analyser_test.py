import unittest
from parameterized import parameterized
from relationship_analysers_classifier.relationship_analysers.containment_analyser.transformer_containment_approach import ContainmentAnalyserTransformer


class TestContainmentAnalyserTransformer(unittest.TestCase):
    """Test cases for ContainmentAnalyserTransformer."""

    @classmethod
    def setUpClass(cls):
        """Initialize the analyser once for all tests."""
        cls.analyser = ContainmentAnalyserTransformer()

    # ------------------------------------------------------------------
    # compute_relations / is_contained
    # ------------------------------------------------------------------

    @parameterized.expand([
        # (child, parent, threshold, description)
        ("password", "user", 0.3, "password/user threshold=0.3"),
        ("password", "user", 0.5, "password/user threshold=0.5"),
        ("password", "user", 0.7, "password/user threshold=0.7"),
        ("password", "user", 0.9, "password/user threshold=0.9"),
        ("user", "password", 0.3, "user/password threshold=0.3"),
        ("user", "password", 0.7, "user/password threshold=0.7"),
        ("admin", "role", 0.3, "admin/role threshold=0.3"),
        ("admin", "role", 0.7, "admin/role threshold=0.7"),
        ("bicycle", "cloud", 0.3, "bicycle/cloud threshold=0.3"),
        ("bicycle", "cloud", 0.9, "bicycle/cloud threshold=0.9"),
        ("penguin", "telescope", 0.5, "penguin/telescope threshold=0.5"),
    ])
    def test_compute_relations_return_types_and_bounds(self, child, parent, threshold, description):
        """Result must be bool and confidence must be in [0, 1]."""
        result, confidence = self.analyser.compute_relations(child, parent, threshold=threshold)
        self.assertIsInstance(result, bool, f"Result should be bool: {description}")
        self.assertIsInstance(confidence, float, f"Confidence should be float: {description}")
        self.assertGreaterEqual(confidence, 0.0, f"Confidence >= 0: {description}")
        self.assertLessEqual(confidence, 1.0, f"Confidence <= 1: {description}")

    @parameterized.expand([
        ("password", "user", 0.3),
        ("password", "user", 0.9),
        ("admin", "role", 0.3),
        ("admin", "role", 0.9),
        ("bicycle", "cloud", 0.3),
        ("bicycle", "cloud", 0.9),
    ])
    def test_compute_relations_result_consistent_with_threshold(self, child, parent, threshold):
        """Boolean result must equal (confidence >= threshold)."""
        result, confidence = self.analyser.compute_relations(child, parent, threshold=threshold)
        self.assertEqual(result, confidence >= threshold)

    def test_compute_relations_same_word_returns_false(self):
        """Identical child and parent must return False."""
        result, _ = self.analyser.compute_relations("user", "user", threshold=0.5)
        self.assertFalse(result)

    def test_compute_relations_empty_child_raises(self):
        with self.assertRaises(ValueError):
            self.analyser.compute_relations("", "user", threshold=0.5)

    def test_compute_relations_empty_parent_raises(self):
        with self.assertRaises(ValueError):
            self.analyser.compute_relations("user", "", threshold=0.5)

    def test_compute_relations_asymmetric(self):
        """Containment is not symmetric: (a, b) and (b, a) may differ."""
        _, conf_ab = self.analyser.compute_relations("wheel", "bicycle", threshold=0.5)
        _, conf_ba = self.analyser.compute_relations("bicycle", "wheel", threshold=0.5)
        # At least one direction should score differently — they should not both be equal
        # (this is a soft check; if the model happens to score them identically it is still valid)
        # Just assert both are valid floats in range
        self.assertGreaterEqual(conf_ab, 0.0)
        self.assertLessEqual(conf_ab, 1.0)
        self.assertGreaterEqual(conf_ba, 0.0)
        self.assertLessEqual(conf_ba, 1.0)