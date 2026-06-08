
import math
import unittest
from unittest.mock import MagicMock, patch

from relationship_analysers_classifier.crud_classifier.gdwg_crud_classifier import CrudAnalyserGdwg
from relationship_analysers_classifier.crud_classifier.crud_actions import CrudAction
from relationship_analysers_classifier.crud_classifier.interface_crud_classifier import InterfaceCrudClassifier


ENV_VARS = {
    "MODEL_GDWG": "test-model",
    "MODEL_KEY_GDWG": "test-api-key",
    "GDWG_API_URL": "https://test.api.url",
    "TEMPERATURE": "0.0",
    "TOP_P": "0.3",
    "MAX_BATCH_SIZE_LLM": "100",
    "GDWG_AI_MODEL_CONTEXT_WINDOWS": "4096",
    "CONTEXT_SAFETY_MARGIN": "0.65",
}


class TestCrudAnalyserGdwg(unittest.TestCase):

    def setUp(self):
        # Clear singleton registry so each test gets a fresh instance
        InterfaceCrudClassifier._instances.clear()

    def _make_classifier(self, mock_client: MagicMock) -> CrudAnalyserGdwg:
        with patch.dict("os.environ", ENV_VARS):
            with patch(
                "relationship_analysers_classifier.crud_classifier.gdwg_crud_classifier.OpenAI",
                return_value=mock_client,
            ):
                return CrudAnalyserGdwg(model="test-model", single_word=True)

    def _make_mock_response(self, content: str) -> MagicMock:
        message = MagicMock()
        message.content = content
        choice = MagicMock()
        choice.message = message
        response = MagicMock()
        response.choices = [choice]
        return response

    # --- classify: happy path ---

    def test_classify_create(self):
        mock_client = MagicMock()
        classifier = self._make_classifier(mock_client)
        mock_client.chat.completions.create.return_value = self._make_mock_response("add -- create")

        action, confidence = classifier.classify("add")

        self.assertEqual(action, CrudAction.CREATE)
        self.assertEqual(confidence, 1.0)

    def test_classify_read(self):
        mock_client = MagicMock()
        classifier = self._make_classifier(mock_client)
        mock_client.chat.completions.create.return_value = self._make_mock_response("retrieve -- read")

        action, confidence = classifier.classify("retrieve")

        self.assertEqual(action, CrudAction.READ)
        self.assertEqual(confidence, 1.0)

    def test_classify_update(self):
        mock_client = MagicMock()
        classifier = self._make_classifier(mock_client)
        mock_client.chat.completions.create.return_value = self._make_mock_response("modify -- update")

        action, confidence = classifier.classify("modify")

        self.assertEqual(action, CrudAction.UPDATE)
        self.assertEqual(confidence, 1.0)

    def test_classify_delete(self):
        mock_client = MagicMock()
        classifier = self._make_classifier(mock_client)
        mock_client.chat.completions.create.return_value = self._make_mock_response("remove -- delete")

        action, confidence = classifier.classify("remove")

        self.assertEqual(action, CrudAction.DELETE)
        self.assertEqual(confidence, 1.0)

    def test_classify_case_insensitive_response(self):
        """Uppercase model response is lowercased before comparison."""
        mock_client = MagicMock()
        classifier = self._make_classifier(mock_client)
        mock_client.chat.completions.create.return_value = self._make_mock_response("ADD -- CREATE")

        action, confidence = classifier.classify("add")

        self.assertEqual(action, CrudAction.CREATE)
        self.assertEqual(confidence, 1.0)

    # --- classify: UNKNOWN cases ---

    def test_classify_unknown_no_separator(self):
        """Response without '--' separator returns UNKNOWN."""
        mock_client = MagicMock()
        classifier = self._make_classifier(mock_client)
        mock_client.chat.completions.create.return_value = self._make_mock_response("create")

        action, confidence = classifier.classify("add")

        self.assertEqual(action, CrudAction.UNKNOWN)
        self.assertEqual(confidence, 0.0)

    def test_classify_unknown_unrecognised_crud_type(self):
        """Unrecognised CRUD type in response returns UNKNOWN."""
        mock_client = MagicMock()
        classifier = self._make_classifier(mock_client)
        mock_client.chat.completions.create.return_value = self._make_mock_response("add -- process")

        action, confidence = classifier.classify("add")

        self.assertEqual(action, CrudAction.UNKNOWN)
        self.assertEqual(confidence, 0.0)

    def test_classify_unknown_empty_first_part(self):
        """Empty first part before '--' returns UNKNOWN."""
        mock_client = MagicMock()
        classifier = self._make_classifier(mock_client)
        mock_client.chat.completions.create.return_value = self._make_mock_response(" -- create")

        action, confidence = classifier.classify("create")

        self.assertEqual(action, CrudAction.UNKNOWN)
        self.assertEqual(confidence, 0.0)

    def test_classify_unknown_empty_second_part(self):
        """Empty second part after '--' returns UNKNOWN."""
        mock_client = MagicMock()
        classifier = self._make_classifier(mock_client)
        mock_client.chat.completions.create.return_value = self._make_mock_response("add -- ")

        action, confidence = classifier.classify("add")

        self.assertEqual(action, CrudAction.UNKNOWN)
        self.assertEqual(confidence, 0.0)

    def test_classify_unknown_too_many_separators(self):
        """More than one '--' results in a split with >2 parts, returning UNKNOWN."""
        mock_client = MagicMock()
        classifier = self._make_classifier(mock_client)
        mock_client.chat.completions.create.return_value = self._make_mock_response("add -- create -- extra")

        action, confidence = classifier.classify("add")

        self.assertEqual(action, CrudAction.UNKNOWN)
        self.assertEqual(confidence, 0.0)

    def test_classify_api_exception_returns_unknown(self):
        """Exception during API call returns UNKNOWN with 0.0 confidence."""
        mock_client = MagicMock()
        classifier = self._make_classifier(mock_client)
        mock_client.chat.completions.create.side_effect = Exception("API error")

        action, confidence = classifier.classify("add")

        self.assertEqual(action, CrudAction.UNKNOWN)
        self.assertEqual(confidence, 0.0)

    # --- classify: return type ---

    def test_classify_returns_tuple(self):
        """classify always returns a (CrudAction, float) tuple."""
        mock_client = MagicMock()
        classifier = self._make_classifier(mock_client)
        mock_client.chat.completions.create.return_value = self._make_mock_response("add -- create")

        result = classifier.classify("add")

        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 2)
        self.assertIsInstance(result[0], CrudAction)
        self.assertIsInstance(result[1], float)

    # --- __init__ / attributes ---

    def test_init_sets_model_name(self):
        """model_name is stored as 'gdwg_{model}'."""
        mock_client = MagicMock()
        classifier = self._make_classifier(mock_client)

        self.assertEqual(classifier.model_name, "gdwg_test-model")

    def test_init_sets_model_name_str(self):
        mock_client = MagicMock()
        classifier = self._make_classifier(mock_client)

        self.assertEqual(classifier.model_name_str, "test-model")

    def test_init_sets_context_window(self):
        """context_windows is floor(tokens * safety_margin)."""
        mock_client = MagicMock()
        classifier = self._make_classifier(mock_client)

        self.assertEqual(classifier.context_windows, math.floor(4096 * 0.65))

    def test_init_single_word_flag(self):
        mock_client = MagicMock()
        classifier = self._make_classifier(mock_client)

        self.assertTrue(classifier.single_word)

    # --- singleton ---

    def test_singleton_returns_same_instance(self):
        """Two calls with the same class return the identical object."""
        mock_client = MagicMock()
        with patch.dict("os.environ", ENV_VARS):
            with patch(
                "relationship_analysers_classifier.crud_classifier.gdwg_crud_classifier.OpenAI",
                return_value=mock_client,
            ):
                first = CrudAnalyserGdwg(model="test-model")
                second = CrudAnalyserGdwg(model="test-model")

        self.assertIs(first, second)