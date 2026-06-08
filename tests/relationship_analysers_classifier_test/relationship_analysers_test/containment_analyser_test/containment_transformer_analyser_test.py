import unittest
from parameterized import parameterized
from relationship_analysers_classifier.relationship_analysers.containment_analyser.transformer_containment_approach import ContainmentAnalyserTransformer


class TestContainmentAnalyserTransformer(unittest.TestCase):
    """Test cases for ContainmentAnalyserTransformer."""
    
    @classmethod
    def setUpClass(cls):
        """Initialize the analyser once for all tests."""
        cls.analyser = ContainmentAnalyserTransformer()
    
    @parameterized.expand([
        # (word_a, word_b, threshold, expected_score, description)
        ("password", "user", 0.3, 0.68, "password/user threshold=0.3"),
        ("password", "user", 0.5, 0.68, "password/user threshold=0.5"),
        ("password", "user", 0.7, 0.68, "password/user threshold=0.7"),
        ("password", "user", 0.9, 0.68, "password/user threshold=0.9"),
        
        ("user", "password", 0.3, 0.35, "user/password threshold=0.3"),
        ("user", "password", 0.5, 0.35, "user/password threshold=0.5"),
        ("user", "password", 0.7, 0.35, "user/password threshold=0.7"),
        ("user", "password", 0.9, 0.35, "user/password threshold=0.9"),
        
        ("admin", "role", 0.3, 0.72, "admin/role threshold=0.3"),
        ("admin", "role", 0.5, 0.72, "admin/role threshold=0.5"),
        ("admin", "role", 0.7, 0.72, "admin/role threshold=0.7"),
        ("admin", "role", 0.9, 0.72, "admin/role threshold=0.9"),
        
        ("action", "verb", 0.3, 0.65, "action/verb threshold=0.3"),
        ("action", "verb", 0.5, 0.65, "action/verb threshold=0.5"),
        ("action", "verb", 0.7, 0.65, "action/verb threshold=0.7"),
        ("action", "verb", 0.9, 0.65, "action/verb threshold=0.9"),
        
        ("bicycle", "cloud", 0.3, 0.12, "bicycle/cloud threshold=0.3"),
        ("bicycle", "cloud", 0.5, 0.12, "bicycle/cloud threshold=0.5"),
        ("bicycle", "cloud", 0.7, 0.12, "bicycle/cloud threshold=0.7"),
        ("bicycle", "cloud", 0.9, 0.12, "bicycle/cloud threshold=0.9"),
        
        ("penguin", "telescope", 0.3, 0.08, "penguin/telescope threshold=0.3"),
        ("penguin", "telescope", 0.5, 0.08, "penguin/telescope threshold=0.5"),
        ("penguin", "telescope", 0.7, 0.08, "penguin/telescope threshold=0.7"),
        ("penguin", "telescope", 0.9, 0.08, "penguin/telescope threshold=0.9"),
    ])
    def test_is_contained(self, word_a, word_b, threshold, expected_score, description):
        """Test is_contained with various word pairs, thresholds, and expected confidence scores."""
        result, confidence = self.analyser.compute_relations(word_a, word_b, threshold=threshold)
        self.assertIsInstance(result, bool, f"Result should be bool: {description}")
        self.assertIsInstance(confidence, float, f"Confidence should be float: {description}")
        self.assertGreaterEqual(confidence, 0.0, f"Confidence should be >= 0: {description}")
        self.assertLessEqual(confidence, 1.0, f"Confidence should be <= 1: {description}")
        # Allow 0.1 tolerance for confidence score
        self.assertAlmostEqual(confidence, expected_score, delta=0.1, msg=f"Expected ~{expected_score:.4f}, got {confidence:.4f}: {description}")
    
    @parameterized.expand([
        ("password", "user", 0.5, 0.62),
        ("admin", "role", 0.5, 0.68),
        ("bicycle", "cloud", 0.8, 0.09),
    ])
    def test_includes(self, word_a, word_b, threshold, expected_score):
        """Test includes relationship."""
        result, confidence = self.analyser.includes(word_a, word_b, threshold)
        self.assertIsInstance(result, bool)
        self.assertIsInstance(confidence, float)
        self.assertGreaterEqual(confidence, 0.0)
        self.assertLessEqual(confidence, 1.0)
        self.assertAlmostEqual(confidence, expected_score, delta=0.1)
    
    @parameterized.expand([
        ("password", "user", 0.5, 0.55),
        ("admin", "organization", 0.5, 0.61),
        ("wheel", "bicycle", 0.5, 0.74),
    ])
    def test_is_part_of(self, word_a, word_b, threshold, expected_score):
        """Test is_part_of relationship."""
        result, confidence = self.analyser.is_part_of(word_a, word_b, threshold)
        self.assertIsInstance(result, bool)
        self.assertIsInstance(confidence, float)
        self.assertGreaterEqual(confidence, 0.0)
        self.assertLessEqual(confidence, 1.0)
        self.assertAlmostEqual(confidence, expected_score, delta=0.1)
    
    @parameterized.expand([
        ("password", "user", 0.5, 0.58),
        ("role", "system", 0.5, 0.63),
    ])
    def test_could_include(self, word_a, word_b, threshold, expected_score):
        """Test could_include conditional relationship."""
        result, confidence = self.analyser.could_include(word_a, word_b, threshold)
        self.assertIsInstance(result, bool)
        self.assertIsInstance(confidence, float)
        self.assertAlmostEqual(confidence, expected_score, delta=0.1)
    
    @parameterized.expand([
        ("permission", "user", 0.5, 0.59),
        ("feature", "system", 0.5, 0.62),
        ("user", "permission", 0.5, 0.59),
        ("system", "feature", 0.5, 0.62),
    ])
    def test_could_be_part_of(self, word_a, word_b, threshold, expected_score):
        """Test could_be_part_of conditional relationship."""
        result, confidence = self.analyser.could_be_part_of(word_a, word_b, threshold)
        self.assertIsInstance(result, bool)
        self.assertIsInstance(confidence, float)
        self.assertAlmostEqual(confidence, expected_score, delta=0.1)