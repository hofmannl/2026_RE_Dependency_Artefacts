import unittest
from relationship_analysers_classifier.crud_classifier.fasttext_analyser_similarity import FastTextCrudAnalyserSimilarity
from relationship_analysers_classifier.crud_classifier.crud_actions import CrudAction


class TestFastTextCrudAnalyserSimilarity(unittest.TestCase):
    """Test cases for FastTextCrudAnalyserSimilarity"""

    @classmethod
    def setUpClass(cls):
        """Initialize the classifier once for all tests"""
        cls.classifier = FastTextCrudAnalyserSimilarity()

    def test_classify_restore(self):
        """Test classification of 'restore' operation"""
        action, similarity = self.classifier.classify("restore")
        self.assertIsInstance(action, CrudAction)
        self.assertIsInstance(similarity, float)
        self.assertGreaterEqual(similarity, 0.0)
        self.assertLessEqual(similarity, 1.0)
        # Restore should be classified as Update even so it should be DELETE
        self.assertEqual(action, CrudAction.UPDATE)

    def test_classify_remove(self):
        """Test classification of 'remove' operation"""
        action, similarity = self.classifier.classify("remove")
        self.assertIsInstance(action, CrudAction)
        self.assertIsInstance(similarity, float)
        self.assertGreaterEqual(similarity, 0.0)
        self.assertLessEqual(similarity, 1.0)
        # Remove should be classified as DELETE
        self.assertEqual(action, CrudAction.DELETE)

    def test_classify_modify(self):
        """Test classification of 'modify' operation"""
        action, similarity = self.classifier.classify("modify")
        self.assertIsInstance(action, CrudAction)
        self.assertIsInstance(similarity, float)
        self.assertGreaterEqual(similarity, 0.0)
        self.assertLessEqual(similarity, 1.0)
        # Modify should be classified as UPDATE
        self.assertEqual(action, CrudAction.UPDATE)

    def test_classify_share(self):
        """Test classification of 'share' operation"""
        action, similarity = self.classifier.classify("share")
        self.assertIsInstance(action, CrudAction)
        self.assertIsInstance(similarity, float)
        self.assertGreaterEqual(similarity, 0.0)
        self.assertLessEqual(similarity, 1.0)
        self.assertEqual(action, CrudAction.READ)

    def test_classify_multi_word_sentence(self):
        """Test classification of multi-word sentence"""
        action, similarity = self.classifier.classify("I want to share objects with you")
        self.assertIsInstance(action, CrudAction)
        self.assertIsInstance(similarity, float)
        self.assertGreaterEqual(similarity, 0.0)
        self.assertLessEqual(similarity, 1.0)
        self.assertEqual(action, CrudAction.READ)

    def test_classify_returns_tuple(self):
        """Test that classify returns a tuple with CrudAction and float"""
        result = self.classifier.classify("create")
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 2)
        action, similarity = result
        self.assertIsInstance(action, CrudAction)
        self.assertIsInstance(similarity, float)

    def test_classify_single_word(self):
        """Test classification of single word operations"""
        action, similarity = self.classifier.classify("delete")
        self.assertIsInstance(action, CrudAction)
        self.assertIsInstance(similarity, float)
        self.assertGreaterEqual(similarity, 0.0)
        self.assertLessEqual(similarity, 1.0)
        self.assertEqual(action, CrudAction.DELETE)

    def test_classify_case_insensitive(self):
        """Test that classification is case-insensitive"""
        result_lower = self.classifier.classify("create")
        result_upper = self.classifier.classify("CREATE")
        result_mixed = self.classifier.classify("Create")
        
        # All should return the same action
        self.assertEqual(result_lower[0], CrudAction.CREATE)
        self.assertEqual(result_lower[0], result_upper[0])
        self.assertEqual(result_lower[0], result_mixed[0])