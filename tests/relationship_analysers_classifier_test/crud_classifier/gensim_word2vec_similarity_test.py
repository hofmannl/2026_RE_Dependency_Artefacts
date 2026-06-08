import unittest
from relationship_analysers_classifier.crud_classifier.gensim_word2vec_similarity import GensimWord2VecCRUDClassifier
from relationship_analysers_classifier.crud_classifier.crud_actions import CrudAction


class TestGensimWord2VecCRUDClassifier(unittest.TestCase):
    """Test cases for GensimWord2VecCRUDClassifier"""

    @classmethod
    def setUpClass(cls):
        """Initialize the classifier once for all tests"""
        cls.classifier = GensimWord2VecCRUDClassifier()

    def test_classify_restore(self):
        """Test classification of 'restore' operation"""
        action, similarity = self.classifier.classify("restore")
        self.assertIsInstance(action, CrudAction)
        self.assertIsInstance(similarity, float)
        self.assertGreaterEqual(similarity, 0.0)
        self.assertLessEqual(similarity, 1.0)
        # Restore should be classified as CREATE
        self.assertEqual(action, CrudAction.CREATE)

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

    def test_classify_multi_word_sentence(self):
        """Test classification of multi-word sentence"""
        action, similarity = self.classifier.classify("I want to share")
        self.assertIsInstance(action, CrudAction)
        self.assertIsInstance(similarity, float)
        self.assertGreaterEqual(similarity, 0.0)
        self.assertLessEqual(similarity, 1.0)
        self.assertEqual(action, CrudAction.CREATE)

    def test_classify_returns_tuple(self):
        """Test that classify returns a tuple with CrudAction and float"""
        result = self.classifier.classify("create")
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 2)
        action, similarity = result
        self.assertIsInstance(action, CrudAction)
        self.assertIsInstance(similarity, float)
        self.assertEqual(action, CrudAction.CREATE)

    def test_classify_out_of_vocabulary(self):
        """Test handling of out-of-vocabulary words"""
        # Using a non-existent word that's unlikely to be in the model
        action, similarity = self.classifier.classify("xyzabc123notaword")
        self.assertEqual(action, CrudAction.UNKNOWN)
        self.assertEqual(similarity, 0.0)
        
    def test_substantiv(self):
        action, similarity = self.classifier.classify("house")
        print(action)
        
        