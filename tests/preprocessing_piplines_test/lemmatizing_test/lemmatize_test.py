import unittest
from parameterized import parameterized
from preprocessing_piplines.lemmatizing.lemmatize import lemmatize_single_word, lemmatize_context_aware_single_words, lemmatize_sentence

class TestLemmatization(unittest.TestCase):
    
    @parameterized.expand([
        ("running", "run"),
        ("playing", "play"),
        ("eating", "eat"),
        ("hike", "hike")
    ])
    def test_lemmatize_single_word(self, word: str, expected: str):
        result = lemmatize_single_word(word)
        self.assertIsInstance(result, str)
        self.assertEqual(result, expected)
        self.assertEqual(result, expected)
    
    @parameterized.expand([
        ("children", "child"),       # often used in education, parent profiles
        ("mice", "mouse"),           # input devices or animal tracking
        ("teeth", "tooth"),          # dental or health apps
        ("feet", "foot"),            # fitness or sizing applications
        ("media", "medium"),         # content, publishing, or marketing
        ("criteria", "criterion"),   # filtering, validation logic
        ("indices", "index"),        # search, databases, finance
        ("statuses", "status"),      # tracking workflows or task states
        ("analyses", "analysis"),    # reporting or business intelligence
        ("theses", "thesis"),        # academic or publishing platforms
        ("diagnoses", "diagnosis"),  # healthcare or bug tracking
        ("phenomena", "phenomenon"), # scientific or observational data
    ])
    def test_lemmatize_single_word_edge_cases(self, word: str, expected: str):
        result = lemmatize_single_word(word)
        self.assertEqual(result, expected)
    
    def test_lemmatize_context_aware_single_words(self):
        result = lemmatize_context_aware_single_words("boys;are;running")
        expected = {"boys": "boy", "are": "be", "running": "run"}
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result, expected)
    
    def test_lemmatize_context_aware_edge_cases(self):
        test_cases = [
            ("running;boys", {"running": "run", "boys": "boy"}),
            ("child;children", {"child": "child", "children": "child"}),
            ("", {}),
            ("single", {"single": "single"})
        ]
        
        for words, expected in test_cases:
            with self.subTest(words=words):
                result = lemmatize_context_aware_single_words(words)
                self.assertEqual(result, expected)
    
    def test_lemmatize_sentence_single_sentence(self):
        sentence = "The boys are running today really fast"
        result = lemmatize_sentence(sentence)
        
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertIsInstance(result[0], dict)
        
        expected_keys = ["the", "boys", "are", "running", "today", "really", "fast"]
        self.assertEqual(set(result[0].keys()), set(expected_keys))
        self.assertEqual(result[0]["boys"], "boy")
        self.assertEqual(result[0]["running"], "run")
        self.assertEqual(result[0]["are"], "be")
    
    def test_lemmatize_sentence_multiple_sentences(self):
        sentences = "The boys are running. The girls are playing."
        result = lemmatize_sentence(sentences)
        
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)
        
        for sent_dict in result:
            self.assertIsInstance(sent_dict, dict)
            for key, value in sent_dict.items():
                self.assertIsInstance(key, str)
                self.assertIsInstance(value, str)
    
    def test_lemmatize_sentence_with_punctuation(self):
        sentence = "Hello, world! How are you?"
        result = lemmatize_sentence(sentence)
        
        self.assertIsInstance(result, list)
        for sent_dict in result:
            for key in sent_dict.keys():
                self.assertNotIn(key, [",", "!", "?"])
    
    def test_caching_behavior(self):
        word = "running"
        result1 = lemmatize_single_word(word)
        result2 = lemmatize_single_word(word)
        self.assertEqual(result1, result2)
        
        context_words = "boys;are;running"
        context_result1 = lemmatize_context_aware_single_words(context_words)
        context_result2 = lemmatize_context_aware_single_words(context_words)
        self.assertEqual(context_result1, context_result2)
        
        sentences = "The kids are playing. Meanwhile the partents are watching. Whereas the dogs are barking."
        sentences1 = lemmatize_sentence(sentences)
        sentences2 = lemmatize_sentence(sentences)
        self.assertEqual(sentences1, sentences2)