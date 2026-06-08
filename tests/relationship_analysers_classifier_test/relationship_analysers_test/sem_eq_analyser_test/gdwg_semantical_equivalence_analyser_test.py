import unittest
from unittest.mock import MagicMock, patch

from relationship_analysers_classifier.relationship_analysers.semantical_equivalence_analyser.gdwg_semantical_equivalence_approach import SemanticEquivalenceAnalyserGdwg
from utilis.annotation_graph_components import TypeGraphUs


ENV_VARS = {
    "MODEL_GDWG": "gpt-3.5-turbo",
    "MODEL_KEY_GDWG": "test-api-key",
    "GDWG_API_URL": "https://test.api.example.com",
    "TEMPERATURE": "0.0",
    "TOP_P": "0.3",
    "MAX_BATCH_SIZE_LLM": "100",
    "GDWG_AI_MODEL_CONTEXT_WINDOWS": "16384",
    "CONTEXT_SAFETY_MARGIN": "0.65",
}

_OPENAI_PATCH = (
    "relationship_analysers_classifier.relationship_analysers"
    ".semantical_equivalence_analyser.gdwg_semantical_equivalence_approach.OpenAI"
)


class TestSemanticEquivalenceAnalyserGdwg(unittest.TestCase):

    def _make_analyser(
        self,
        mock_client: MagicMock,
        typ: TypeGraphUs = TypeGraphUs.ENTITY,
        extra_env: dict | None = None,
    ) -> SemanticEquivalenceAnalyserGdwg:
        env = {**ENV_VARS, **(extra_env or {})}
        with patch.dict("os.environ", env):
            with patch(_OPENAI_PATCH, return_value=mock_client):
                return SemanticEquivalenceAnalyserGdwg(
                    model=env["MODEL_GDWG"], typ=typ
                )

    def _make_mock_response(self, content: str) -> MagicMock:
        message = MagicMock()
        message.content = content
        choice = MagicMock()
        choice.message = message
        response = MagicMock()
        response.choices = [choice]
        return response

    # ------------------------------------------------------------------
    # are_contained: happy path
    # ------------------------------------------------------------------

    def test_are_contained_returns_true(self):
        """A semantically equivalent pair returns True."""
        mock_client = MagicMock()
        analyser = self._make_analyser(mock_client)
        mock_client.chat.completions.create.return_value = self._make_mock_response(
            "login--sign in--true"
        )

        result = analyser.are_contained({("login", "sign in")})

        self.assertEqual(len(result), 1)
        subject, obj, equivalent = result[0]
        self.assertEqual(subject, "login")
        self.assertEqual(obj, "sign in")
        self.assertTrue(equivalent)

    def test_are_contained_returns_false(self):
        """A pair that is not semantically equivalent returns False."""
        mock_client = MagicMock()
        analyser = self._make_analyser(mock_client)
        mock_client.chat.completions.create.return_value = self._make_mock_response(
            "login--delete--false"
        )

        result = analyser.are_contained({("login", "delete")})

        self.assertEqual(len(result), 1)
        self.assertFalse(result[0][2])

    def test_are_contained_multiple_pairs(self):
        """All pairs from a multi-pair batch are returned."""
        mock_client = MagicMock()
        analyser = self._make_analyser(mock_client)
        mock_client.chat.completions.create.return_value = self._make_mock_response(
            "login--sign in--true\ndelete--remove--true"
        )

        result = analyser.are_contained({("login", "sign in"), ("delete", "remove")})

        self.assertEqual(len(result), 2)
        result_map = {(r[0], r[1]): r[2] for r in result}
        self.assertTrue(result_map[("login", "sign in")])
        self.assertTrue(result_map[("delete", "remove")])

    def test_are_contained_case_insensitive_true(self):
        """Mixed-case 'True' in the response is treated as True."""
        mock_client = MagicMock()
        analyser = self._make_analyser(mock_client)
        mock_client.chat.completions.create.return_value = self._make_mock_response(
            "login--sign in--True"
        )

        result = analyser.are_contained({("login", "sign in")})

        self.assertTrue(result[0][2])

    # ------------------------------------------------------------------
    # compute_relations delegates to are_contained
    # ------------------------------------------------------------------

    def test_compute_relations_delegates(self):
        """compute_relations returns the same result as are_contained."""
        mock_client = MagicMock()
        analyser = self._make_analyser(mock_client)
        mock_client.chat.completions.create.return_value = self._make_mock_response(
            "view--display--true"
        )

        result = analyser.compute_relations({("view", "display")})

        self.assertEqual(len(result), 1)
        self.assertTrue(result[0][2])

    # ------------------------------------------------------------------
    # TypeGraphUs variants
    # ------------------------------------------------------------------

    def test_entity_type_calls_api(self):
        """Analyser initialised with ENTITY type sends a request without error."""
        mock_client = MagicMock()
        analyser = self._make_analyser(mock_client, typ=TypeGraphUs.ENTITY)
        mock_client.chat.completions.create.return_value = self._make_mock_response(
            "user--member--true"
        )

        result = analyser.are_contained({("user", "member")})

        mock_client.chat.completions.create.assert_called_once()
        self.assertEqual(len(result), 1)

    def test_action_type_calls_api(self):
        """Analyser initialised with ACTION type sends a request without error."""
        mock_client = MagicMock()
        analyser = self._make_analyser(mock_client, typ=TypeGraphUs.ACTION)
        mock_client.chat.completions.create.return_value = self._make_mock_response(
            "login--sign in--true"
        )

        result = analyser.are_contained({("login", "sign in")})

        mock_client.chat.completions.create.assert_called_once()
        self.assertEqual(len(result), 1)

    # ------------------------------------------------------------------
    # Error handling
    # ------------------------------------------------------------------

    def test_are_contained_api_error_returns_error_tuple(self):
        """When the API raises an exception each pair is returned with 'error'."""
        mock_client = MagicMock()
        analyser = self._make_analyser(mock_client)
        mock_client.chat.completions.create.side_effect = Exception("API failure")

        result = analyser.are_contained({("login", "sign in")})

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], ("login", "sign in", "error"))

    def test_are_contained_api_error_multiple_pairs_all_returned_as_error(self):
        """All pairs in a failing batch get an 'error' result."""
        mock_client = MagicMock()
        analyser = self._make_analyser(mock_client)
        mock_client.chat.completions.create.side_effect = Exception("API failure")

        pairs = {("login", "sign in"), ("delete", "remove")}
        result = analyser.are_contained(pairs)

        self.assertEqual(len(result), 2)
        for r in result:
            self.assertEqual(r[2], "error")

    # ------------------------------------------------------------------
    # Batch splitting
    # ------------------------------------------------------------------

    def test_are_contained_respects_max_batch_size(self):
        """When max_batch_size=1 each pair triggers its own API call."""
        mock_client = MagicMock()
        analyser = self._make_analyser(mock_client, extra_env={"MAX_BATCH_SIZE_LLM": "1"})
        mock_client.chat.completions.create.side_effect = [
            self._make_mock_response("login--sign in--true"),
            self._make_mock_response("delete--remove--false"),
        ]

        result = analyser.are_contained({("login", "sign in"), ("delete", "remove")})

        self.assertEqual(mock_client.chat.completions.create.call_count, 2)
        self.assertEqual(len(result), 2)

    # ------------------------------------------------------------------
    # Reprompt for missing pairs
    # ------------------------------------------------------------------

    def test_are_contained_reprompts_for_missing_pair(self):
        """Pairs missing from the LLM response trigger a reprompt call."""
        mock_client = MagicMock()
        analyser = self._make_analyser(mock_client)

        # First call omits (delete, remove); second call (reprompt) covers it
        mock_client.chat.completions.create.side_effect = [
            self._make_mock_response("login--sign in--true"),
            self._make_mock_response("delete--remove--false"),
        ]

        result = analyser.are_contained({("login", "sign in"), ("delete", "remove")})

        self.assertEqual(mock_client.chat.completions.create.call_count, 2)
        result_map = {(r[0], r[1]): r[2] for r in result}
        self.assertTrue(result_map[("login", "sign in")])
        self.assertFalse(result_map[("delete", "remove")])

    # ------------------------------------------------------------------
    # Empty input
    # ------------------------------------------------------------------

    def test_are_contained_empty_set_returns_empty(self):
        """An empty input set returns an empty list without calling the API."""
        mock_client = MagicMock()
        analyser = self._make_analyser(mock_client)

        result = analyser.are_contained(set())

        mock_client.chat.completions.create.assert_not_called()
        self.assertEqual(result, [])
