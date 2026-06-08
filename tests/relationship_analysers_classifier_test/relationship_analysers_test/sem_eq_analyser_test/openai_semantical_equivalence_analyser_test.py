import unittest
from unittest.mock import MagicMock, patch

from relationship_analysers_classifier.relationship_analysers.semantical_equivalence_analyser.openai_semantical_equivalence_approach import SemanticEquivalenceAnalyserOpenAI
from utilis.annotation_graph_components import TypeGraphUs


ENV_VARS = {
    "OPENAI_MODEL": "gpt-4o-mini",
    "MODEL_KEY_OPENAI": "test-api-key",
    "TEMPERATURE": "0.0",
    "TOP_P": "0.3",
    "MAX_BATCH_SIZE_LLM": "100",
    "OPEN_AI_MODEL_CONTEXT_WINDOWS": "16384",
    "CONTEXT_SAFETY_MARGIN": "0.65",
}

_PATCH_OPENAI = (
    "relationship_analysers_classifier.relationship_analysers"
    ".semantical_equivalence_analyser.openai_semantical_equivalence_approach.OpenAI"
)


class TestSemanticEquivalenceAnalyserOpenAI(unittest.TestCase):

    def _make_analyser(
        self,
        mock_client: MagicMock,
        typ: TypeGraphUs = TypeGraphUs.ENTITY,
    ) -> SemanticEquivalenceAnalyserOpenAI:
        with patch.dict("os.environ", ENV_VARS):
            with patch(_PATCH_OPENAI, return_value=mock_client):
                return SemanticEquivalenceAnalyserOpenAI(
                    model="gpt-4o-mini", typ=typ
                )

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
        """A pair of semantically equivalent entities returns True."""
        mock_client = MagicMock()
        analyser = self._make_analyser(mock_client)
        mock_client.chat.completions.create.return_value = self._make_mock_response(
            "user--customer--true"
        )

        result = analyser.are_contained({("user", "customer")})

        self.assertEqual(len(result), 1)
        subject, obj, equivalent = result[0]
        self.assertEqual(subject, "user")
        self.assertEqual(obj, "customer")
        self.assertTrue(equivalent)

    def test_are_contained_returns_false(self):
        """A pair of non-equivalent entities returns False."""
        mock_client = MagicMock()
        analyser = self._make_analyser(mock_client)
        mock_client.chat.completions.create.return_value = self._make_mock_response(
            "user--admin--false"
        )

        result = analyser.are_contained({("user", "admin")})

        self.assertEqual(len(result), 1)
        subject, obj, equivalent = result[0]
        self.assertFalse(equivalent)

    def test_are_contained_multiple_pairs(self):
        """Multiple pairs are all processed and returned."""
        mock_client = MagicMock()
        analyser = self._make_analyser(mock_client)
        mock_client.chat.completions.create.return_value = self._make_mock_response(
            "user--customer--true\norder--purchase--true"
        )

        result = analyser.are_contained({("user", "customer"), ("order", "purchase")})

        self.assertEqual(len(result), 2)
        result_map = {(r[0], r[1]): r[2] for r in result}
        self.assertTrue(result_map[("user", "customer")])
        self.assertTrue(result_map[("order", "purchase")])

    def test_are_contained_case_insensitive_true(self):
        """The string 'True' (mixed case) in the response is treated as True."""
        mock_client = MagicMock()
        analyser = self._make_analyser(mock_client)
        mock_client.chat.completions.create.return_value = self._make_mock_response(
            "user--customer--True"
        )

        result = analyser.are_contained({("user", "customer")})

        self.assertTrue(result[0][2])

    # --- compute_relations delegates to are_contained ---

    def test_compute_relations_delegates(self):
        """compute_relations returns the same result as are_contained."""
        mock_client = MagicMock()
        analyser = self._make_analyser(mock_client)
        mock_client.chat.completions.create.return_value = self._make_mock_response(
            "user--customer--true"
        )

        result = analyser.compute_relations({("user", "customer")})

        self.assertEqual(len(result), 1)
        self.assertTrue(result[0][2])

    # --- typ parameter ---

    def test_init_with_action_type(self):
        """Analyser initialises correctly with TypeGraphUs.ACTION."""
        mock_client = MagicMock()
        analyser = self._make_analyser(mock_client, typ=TypeGraphUs.ACTION)
        self.assertEqual(analyser.typ, TypeGraphUs.ACTION)

    def test_init_with_persona_type(self):
        """Analyser initialises correctly with TypeGraphUs.PERSONA."""
        mock_client = MagicMock()
        analyser = self._make_analyser(mock_client, typ=TypeGraphUs.PERSONA)
        self.assertEqual(analyser.typ, TypeGraphUs.PERSONA)

    def test_action_typ_used_in_api_call(self):
        """When typ=ACTION an API call is made and the result is returned."""
        mock_client = MagicMock()
        analyser = self._make_analyser(mock_client, typ=TypeGraphUs.ACTION)
        mock_client.chat.completions.create.return_value = self._make_mock_response(
            "login--sign in--true"
        )

        result = analyser.are_contained({("login", "sign in")})

        mock_client.chat.completions.create.assert_called_once()
        self.assertTrue(result[0][2])

    # --- error handling ---

    def test_are_contained_api_error_returns_error_tuple(self):
        """When the OpenAI API raises an exception each pair gets an 'error' result."""
        mock_client = MagicMock()
        analyser = self._make_analyser(mock_client)
        mock_client.chat.completions.create.side_effect = Exception("API failure")

        result = analyser.are_contained({("user", "customer")})

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], ("user", "customer", "error"))

    # --- batch splitting ---

    def test_are_contained_respects_max_batch_size(self):
        """When max_batch_size=1 each pair is sent in a separate API call."""
        mock_client = MagicMock()
        with patch.dict("os.environ", {**ENV_VARS, "MAX_BATCH_SIZE_LLM": "1"}):
            with patch(_PATCH_OPENAI, return_value=mock_client):
                analyser = SemanticEquivalenceAnalyserOpenAI(
                    model="gpt-4o-mini", typ=TypeGraphUs.ENTITY
                )

        mock_client.chat.completions.create.side_effect = [
            self._make_mock_response("user--customer--true"),
            self._make_mock_response("order--purchase--false"),
        ]

        result = analyser.are_contained({("user", "customer"), ("order", "purchase")})

        self.assertEqual(mock_client.chat.completions.create.call_count, 2)
        self.assertEqual(len(result), 2)

    # --- reprompt for missing pairs ---

    def test_are_contained_reprompts_for_missing_pair(self):
        """Missing pairs in the LLM response trigger a reprompt call."""
        mock_client = MagicMock()
        analyser = self._make_analyser(mock_client)

        # First call omits (order, purchase); second call (reprompt) provides it
        mock_client.chat.completions.create.side_effect = [
            self._make_mock_response("user--customer--true"),
            self._make_mock_response("order--purchase--false"),
        ]

        result = analyser.are_contained({("user", "customer"), ("order", "purchase")})

        self.assertEqual(mock_client.chat.completions.create.call_count, 2)
        result_map = {(r[0], r[1]): r[2] for r in result}
        self.assertTrue(result_map[("user", "customer")])
        self.assertFalse(result_map[("order", "purchase")])

    # --- empty input ---

    def test_are_contained_empty_set_returns_empty(self):
        """An empty input set returns an empty list without calling the API."""
        mock_client = MagicMock()
        analyser = self._make_analyser(mock_client)

        result = analyser.are_contained(set())

        mock_client.chat.completions.create.assert_not_called()
        self.assertEqual(result, [])
