import unittest
from unittest.mock import MagicMock, patch

from relationship_analysers_classifier.relationship_analysers.containment_analyser.openai_containment_approach import ContainmentAnalyserOpenAI


ENV_VARS = {
    "OPENAI_MODEL": "gpt-4o-mini",
    "MODEL_KEY_OPENAI": "test-api-key",
    "TEMPERATURE": "0.0",
    "TOP_P": "0.3",
    "MAX_BATCH_SIZE_LLM": "100",
    "OPEN_AI_MODEL_CONTEXT_WINDOWS": "16384",
    "CONTEXT_SAFETY_MARGIN": "0.65",
}


class TestContainmentAnalyserOpenAI(unittest.TestCase):

    def _make_analyser(self, mock_client: MagicMock) -> ContainmentAnalyserOpenAI:
        with patch.dict("os.environ", ENV_VARS):
            with patch(
                "relationship_analysers_classifier.relationship_analysers.containment_analyser.openai_containment_approach.OpenAI",
                return_value=mock_client,
            ):
                return ContainmentAnalyserOpenAI(model="gpt-4o-mini")

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
        """When the OpenAI API raises an exception each pair gets an 'error' result."""
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
                "relationship_analysers_classifier.relationship_analysers.containment_analyser.openai_containment_approach.OpenAI",
                return_value=mock_client,
            ):
                analyser = ContainmentAnalyserOpenAI(model="gpt-4o-mini")

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

        self.assertEqual(mock_client.chat.completions.create.call_count, 2)
        result_map = {(r[0], r[1]): r[2] for r in result}
        self.assertTrue(result_map[("profile", "password")])
        self.assertFalse(result_map[("order", "item")])

    # --- empty input ---

    def test_are_contained_empty_set_returns_empty(self):
        """An empty input set returns an empty list without calling the API."""
        mock_client = MagicMock()
        analyser = self._make_analyser(mock_client)

        result = analyser.are_contained(set())

        mock_client.chat.completions.create.assert_not_called()
        self.assertEqual(result, [])
