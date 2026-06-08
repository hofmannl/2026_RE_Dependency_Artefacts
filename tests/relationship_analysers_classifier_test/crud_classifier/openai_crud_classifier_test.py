import math
import unittest
from unittest.mock import MagicMock, patch

from relationship_analysers_classifier.crud_classifier.crud_actions import CrudAction
from relationship_analysers_classifier.crud_classifier.interface_crud_classifier import InterfaceCrudClassifier


ENV_DEFAULTS = {
    "MODEL_OPENAI": "gpt-3.5-turbo",
    "TEMPERATURE": "0.0",
    "TOP_P": "0.3",
    "MAX_BATCH_SIZE_LLM": "100",
    "OPEN_AI_MODEL_CONTEXT_WINDOWS": "16385",
    "CONTEXT_SAFETY_MARGIN": "0.65",
}


def _make_response(content: str) -> MagicMock:
    """Helper to build a mock OpenAI chat completion response."""
    response = MagicMock()
    response.choices[0].message.content = content
    return response


class TestCrudAnalyserOpenAI(unittest.TestCase):

    def setUp(self):
        """Clear the singleton registry before every test."""
        InterfaceCrudClassifier._instances.clear()

    def _build_classifier(self, extra_env: dict | None = None):
        """Construct a CrudAnalyserOpenAI with all external dependencies patched."""
        env = {**ENV_DEFAULTS, **(extra_env or {})}

        with patch.dict("os.environ", env, clear=False), \
             patch("relationship_analysers_classifier.crud_classifier.openai_crud_classifier.OpenAI") as mock_openai, \
             patch("relationship_analysers_classifier.crud_classifier.openai_crud_classifier.tiktoken") as mock_tiktoken, \
             patch("relationship_analysers_classifier.crud_classifier.openai_crud_classifier.dotenv.load_dotenv"):

            mock_tiktoken.encoding_for_model.return_value = MagicMock()
            mock_client = MagicMock()
            mock_openai.return_value = mock_client

            from relationship_analysers_classifier.crud_classifier.openai_crud_classifier import CrudAnalyserOpenAI
            classifier = CrudAnalyserOpenAI(model="gpt-3.5-turbo")

        return classifier, mock_client

    # ------------------------------------------------------------------
    # Initialisation
    # ------------------------------------------------------------------

    def test_model_name_is_prefixed(self):
        classifier, _ = self._build_classifier()
        self.assertEqual(classifier.model_name, "openai_gpt-3.5-turbo")

    def test_model_name_str_stored(self):
        classifier, _ = self._build_classifier()
        self.assertEqual(classifier.model_name_str, "gpt-3.5-turbo")

    def test_context_window_computed(self):
        classifier, _ = self._build_classifier()
        expected = math.floor(16385 * 0.65)
        self.assertEqual(classifier.context_windows, expected)

    def test_max_batch_size_default(self):
        classifier, _ = self._build_classifier()
        self.assertEqual(classifier.max_batch_size, 100)

    def test_tiktoken_fallback_encoding(self):
        """When encoding_for_model raises, cl100k_base is used."""
        env = ENV_DEFAULTS.copy()
        with patch.dict("os.environ", env, clear=False), \
             patch("relationship_analysers_classifier.crud_classifier.openai_crud_classifier.OpenAI"), \
             patch("relationship_analysers_classifier.crud_classifier.openai_crud_classifier.tiktoken") as mock_tiktoken, \
             patch("relationship_analysers_classifier.crud_classifier.openai_crud_classifier.dotenv.load_dotenv"):

            mock_tiktoken.encoding_for_model.side_effect = Exception("unknown model")
            fallback_enc = MagicMock()
            mock_tiktoken.get_encoding.return_value = fallback_enc

            from relationship_analysers_classifier.crud_classifier.openai_crud_classifier import CrudAnalyserOpenAI
            classifier = CrudAnalyserOpenAI(model="unknown-model")

        mock_tiktoken.get_encoding.assert_called_once_with("cl100k_base")
        self.assertEqual(classifier.encoding, fallback_enc)

    # ------------------------------------------------------------------
    # classify – happy paths
    # ------------------------------------------------------------------

    def test_classify_create(self):
        classifier, mock_client = self._build_classifier()
        mock_client.chat.completions.create.return_value = _make_response("add -- create")
        action, confidence = classifier.classify("add")
        self.assertEqual(action, CrudAction.CREATE)
        self.assertEqual(confidence, 1.0)

    def test_classify_read(self):
        classifier, mock_client = self._build_classifier()
        mock_client.chat.completions.create.return_value = _make_response("get -- read")
        action, confidence = classifier.classify("get")
        self.assertEqual(action, CrudAction.READ)
        self.assertEqual(confidence, 1.0)

    def test_classify_update(self):
        classifier, mock_client = self._build_classifier()
        mock_client.chat.completions.create.return_value = _make_response("modify -- update")
        action, confidence = classifier.classify("modify")
        self.assertEqual(action, CrudAction.UPDATE)
        self.assertEqual(confidence, 1.0)

    def test_classify_delete(self):
        classifier, mock_client = self._build_classifier()
        mock_client.chat.completions.create.return_value = _make_response("remove -- delete")
        action, confidence = classifier.classify("remove")
        self.assertEqual(action, CrudAction.DELETE)
        self.assertEqual(confidence, 1.0)

    def test_classify_returns_tuple(self):
        classifier, mock_client = self._build_classifier()
        mock_client.chat.completions.create.return_value = _make_response("create -- create")
        result = classifier.classify("create")
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 2)

    def test_classify_confidence_is_float(self):
        classifier, mock_client = self._build_classifier()
        mock_client.chat.completions.create.return_value = _make_response("delete -- delete")
        _, confidence = classifier.classify("delete")
        self.assertIsInstance(confidence, float)

    def test_classify_response_strips_whitespace(self):
        """Extra whitespace around the CRUD type should be handled."""
        classifier, mock_client = self._build_classifier()
        mock_client.chat.completions.create.return_value = _make_response("update --  update  ")
        action, _ = classifier.classify("update")
        self.assertEqual(action, CrudAction.UPDATE)

    def test_classify_response_case_insensitive(self):
        """Response is lowercased before comparison."""
        classifier, mock_client = self._build_classifier()
        mock_client.chat.completions.create.return_value = _make_response("Create -- CREATE")
        action, _ = classifier.classify("Create")
        self.assertEqual(action, CrudAction.CREATE)

    # ------------------------------------------------------------------
    # classify – edge / failure cases
    # ------------------------------------------------------------------

    def test_classify_unknown_crud_type(self):
        """An unrecognised CRUD label returns UNKNOWN."""
        classifier, mock_client = self._build_classifier()
        mock_client.chat.completions.create.return_value = _make_response("do -- execute")
        action, confidence = classifier.classify("do")
        self.assertEqual(action, CrudAction.UNKNOWN)
        self.assertEqual(confidence, 0.0)

    def test_classify_malformed_response_no_separator(self):
        """Response without '--' separator returns UNKNOWN."""
        classifier, mock_client = self._build_classifier()
        mock_client.chat.completions.create.return_value = _make_response("create")
        action, confidence = classifier.classify("create")
        self.assertEqual(action, CrudAction.UNKNOWN)
        self.assertEqual(confidence, 0.0)

    def test_classify_malformed_response_empty_parts(self):
        """Response with empty segment on one side of '--' returns UNKNOWN."""
        classifier, mock_client = self._build_classifier()
        mock_client.chat.completions.create.return_value = _make_response("-- create")
        action, confidence = classifier.classify("create")
        self.assertEqual(action, CrudAction.UNKNOWN)
        self.assertEqual(confidence, 0.0)

    def test_classify_api_exception_returns_unknown(self):
        """An exception from the API call returns UNKNOWN with zero confidence."""
        classifier, mock_client = self._build_classifier()
        mock_client.chat.completions.create.side_effect = Exception("network error")
        action, confidence = classifier.classify("add")
        self.assertEqual(action, CrudAction.UNKNOWN)
        self.assertEqual(confidence, 0.0)

    def test_classify_api_called_with_correct_model(self):
        """The model name string is forwarded to the API."""
        classifier, mock_client = self._build_classifier()
        mock_client.chat.completions.create.return_value = _make_response("add -- create")
        classifier.classify("add")
        call_kwargs = mock_client.chat.completions.create.call_args
        self.assertEqual(call_kwargs.kwargs["model"], "gpt-3.5-turbo")

    def test_classify_temperature_forwarded(self):
        classifier, mock_client = self._build_classifier()
        mock_client.chat.completions.create.return_value = _make_response("add -- create")
        classifier.classify("add")
        call_kwargs = mock_client.chat.completions.create.call_args
        self.assertEqual(call_kwargs.kwargs["temperature"], 0.0)

    def test_classify_top_p_forwarded(self):
        classifier, mock_client = self._build_classifier()
        mock_client.chat.completions.create.return_value = _make_response("add -- create")
        classifier.classify("add")
        call_kwargs = mock_client.chat.completions.create.call_args
        self.assertEqual(call_kwargs.kwargs["top_p"], 0.3)

    # ------------------------------------------------------------------
    # Singleton behaviour
    # ------------------------------------------------------------------

    def test_singleton_returns_same_instance(self):
        classifier1, _ = self._build_classifier()
        instance_a = InterfaceCrudClassifier._instances.get(type(classifier1))
        self.assertIs(classifier1, instance_a)

    def test_reset_removes_instance(self):
        classifier, _ = self._build_classifier()
        cls = type(classifier)
        self.assertIn(cls, InterfaceCrudClassifier._instances)
        classifier.reset_crud_classifier(instance_class=cls)
        self.assertNotIn(cls, InterfaceCrudClassifier._instances)