import unittest
from unittest.mock import MagicMock, patch

from relationship_analysers_classifier.relationship_analysers.containment_analyser.gdwg_containment_approach import ContainmentAnalyserGdwg


ENV_VARS = {
    "MODEL_GDWG": "gdwg-model",
    "MODEL_KEY_GDWG": "test-api-key",
    "GDWG_API_URL": "https://fake-gdwg-api.example.com",
    "TEMPERATURE": "0.0",
    "TOP_P": "0.3",
    "MAX_BATCH_SIZE_LLM": "100",
    "GDWG_AI_MODEL_CONTEXT_WINDOWS": "16384",
    "CONTEXT_SAFETY_MARGIN": "0.65",
}


class TestContainmentAnalyserGdwg(unittest.TestCase):

    def _make_analyser(self, mock_client: MagicMock) -> ContainmentAnalyserGdwg:
        with patch.dict("os.environ", ENV_VARS):
            with patch(
                "relationship_analysers_classifier.relationship_analysers.containment_analyser.gdwg_containment_approach.OpenAI",
                return_value=mock_client,
            ):
                return ContainmentAnalyserGdwg(model="gdwg-model")

    def _make_mock_response(self, content: str) -> MagicMock:
        message = MagicMock()
        message.content = content
        choice = MagicMock()
        choice.message = message
        response = MagicMock()
        response.choices = [choice]
        return response

    # --- are_contained: happy path ---

    def test_are_contained_returns_true(self):
        """A pair where entity2 is contained in entity1 returns True."""
        mock_client = MagicMock()
        analyser = self._make_analyser(mock_client)
        mock_client.chat.completions.create.return_value = self._make_mock_response(
            "profile--password--true"
        )

        result = analyser.are_contained({("profile", "password")})

        self.assertEqual(len(result), 1)
        subject, obj, contained = result[0]
        self.assertEqual(subject, "profile")
        self.assertEqual(obj, "password")
        self.assertTrue(contained)

    def test_are_contained_returns_false(self):
        """A pair where entity2 is not contained in entity1 returns False."""
        mock_client = MagicMock()
        analyser = self._make_analyser(mock_client)
        mock_client.chat.completions.create.return_value = self._make_mock_response(
            "password--profile--false"
        )

        result = analyser.are_contained({("password", "profile")})

        self.assertEqual(len(result), 1)
        subject, obj, contained = result[0]
        self.assertFalse(contained)

    def test_are_contained_multiple_pairs(self):
        """Multiple pairs are all processed and returned."""
        mock_client = MagicMock()
        analyser = self._make_analyser(mock_client)
        mock_client.chat.completions.create.return_value = self._make_mock_response(
            "profile--password--true\norder--item--true"
        )

        result = analyser.are_contained({("profile", "password"), ("order", "item")})

        self.assertEqual(len(result), 2)
        result_map = {(r[0], r[1]): r[2] for r in result}
        self.assertTrue(result_map[("profile", "password")])
        self.assertTrue(result_map[("order", "item")])

    def test_are_contained_case_insensitive_true(self):
        """The string 'True' (mixed case) in the response is treated as True."""
        mock_client = MagicMock()
        analyser = self._make_analyser(mock_client)
        mock_client.chat.completions.create.return_value = self._make_mock_response(
            "profile--password--True"
        )

        result = analyser.are_contained({("profile", "password")})

        self.assertTrue(result[0][2])

    # --- compute_relations delegates to are_contained ---

    def test_compute_relations_delegates(self):
        """compute_relations returns same result as are_contained."""
        mock_client = MagicMock()
        analyser = self._make_analyser(mock_client)
        mock_client.chat.completions.create.return_value = self._make_mock_response(
            "cart--product--true"
        )

        result = analyser.compute_relations({("cart", "product")})

        self.assertEqual(len(result), 1)
        self.assertTrue(result[0][2])

    # --- error handling ---

    def test_are_contained_api_error_returns_error_tuple(self):
        """When the GDWG API raises an exception each pair gets an 'error' result."""
        mock_client = MagicMock()
        analyser = self._make_analyser(mock_client)
        mock_client.chat.completions.create.side_effect = Exception("API failure")

        result = analyser.are_contained({("profile", "password")})

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], ("profile", "password", "error"))

    # --- batch splitting ---

    def test_are_contained_respects_max_batch_size(self):
        """When max_batch_size=1 each pair is sent in a separate API call."""
        mock_client = MagicMock()
        with patch.dict("os.environ", {**ENV_VARS, "MAX_BATCH_SIZE_LLM": "1"}):
            with patch(
                "relationship_analysers_classifier.relationship_analysers.containment_analyser.gdwg_containment_approach.OpenAI",
                return_value=mock_client,
            ):
                analyser = ContainmentAnalyserGdwg(model="gdwg-model")

        mock_client.chat.completions.create.side_effect = [
            self._make_mock_response("profile--password--true"),
            self._make_mock_response("order--item--false"),
        ]

        result = analyser.are_contained({("profile", "password"), ("order", "item")})

        self.assertEqual(mock_client.chat.completions.create.call_count, 2)
        self.assertEqual(len(result), 2)

    # --- reprompt for missing pairs ---

    def test_are_contained_reprompts_for_missing_pair(self):
        """Missing pairs in the LLM response trigger a reprompt call."""
        mock_client = MagicMock()
        analyser = self._make_analyser(mock_client)

        # First call omits (order, item); second call (reprompt) provides it
        mock_client.chat.completions.create.side_effect = [
            self._make_mock_response("profile--password--true"),
            self._make_mock_response("order--item--false"),
        ]

        result = analyser.are_contained({("profile", "password"), ("order", "item")})

        self.assertGreaterEqual(mock_client.chat.completions.create.call_count, 2)
        result_map = {(r[0], r[1]): r[2] for r in result}
        self.assertTrue(result_map[("profile", "password")])
        self.assertFalse(result_map[("order", "item")])

    # --- empty batch guard ---

    def test_are_contained_raises_on_single_oversized_pair(self):
        """A pair that exceeds the context window on its own raises ValueError."""
        mock_client = MagicMock()
        with patch.dict("os.environ", {**ENV_VARS, "GDWG_AI_MODEL_CONTEXT_WINDOWS": "1", "CONTEXT_SAFETY_MARGIN": "1.0"}):
            with patch(
                "relationship_analysers_classifier.relationship_analysers.containment_analyser.gdwg_containment_approach.OpenAI",
                return_value=mock_client,
            ):
                analyser = ContainmentAnalyserGdwg(model="gdwg-model")

        with self.assertRaises(ValueError):
            analyser.are_contained({("profile", "password")})

    # --- __init__: context window calculation ---

    def test_init_context_window_applied_safety_margin(self):
        """context_windows is floored to tokens * safety_margin."""
        mock_client = MagicMock()
        with patch.dict("os.environ", {**ENV_VARS, "GDWG_AI_MODEL_CONTEXT_WINDOWS": "1000", "CONTEXT_SAFETY_MARGIN": "0.5"}):
            with patch(
                "relationship_analysers_classifier.relationship_analysers.containment_analyser.gdwg_containment_approach.OpenAI",
                return_value=mock_client,
            ):
                analyser = ContainmentAnalyserGdwg(model="gdwg-model")

        self.assertEqual(analyser.context_windows, 500)

    # --- __init__: fallback encoding ---

    def test_init_uses_fallback_encoding_for_unknown_model(self):
        """An unknown model name falls back to the cl100k_base encoding without raising."""
        mock_client = MagicMock()
        with patch.dict("os.environ", ENV_VARS):
            with patch(
                "relationship_analysers_classifier.relationship_analysers.containment_analyser.gdwg_containment_approach.OpenAI",
                return_value=mock_client,
            ):
                analyser = ContainmentAnalyserGdwg(model="unknown-model-xyz")

        self.assertIsNotNone(analyser.encoding)