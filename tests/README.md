# Test Suite

## Quick Commands

```bash
# Run all tests
python -m unittest discover -s tests -p "*_test.py"

# Run with coverage
coverage run --source=src -m unittest discover -s tests -p "*_test.py" # Just statement and line 
coverage run --branch --source=src -m unittest discover -s tests -p "*_test.py" # also branch coverage
coverage report           # Terminal output
coverage html            # Generate HTML report
open htmlcov/index.html  # View in browser
```

## Structure

```
tests/
├── computation_of_dependencies_test/
│   └── order_dependencies_test.py (both dependency variations)
├── preprocessing_piplines_test/
│   ├── template_based_splitter_test.py
│   └── lemmatizing_test/
│       └── lemmatize_test.py
├── relationship_analysers_classifier_test/
│   ├── crud_classifier/
│   │   ├── fasttext_similarity_test.py
│   │   ├── gdwg_crud_classifier_test.py
│   │   ├── gensim_word2vec_similarity_test.py
│   │   └── openai_crud_classifier_test.py
│   ├── relationship_analysers_test/
│   │   ├── containment_analyser_test/
│   │   │   ├── containment_transformer_analyser_test.py
│   │   │   ├── gdwg_containment_analyser_test.py
│   │   │   └── openai_containment_analyser_test.py
│   │   └── sem_eq_analyser_test/
│   │       ├── gdwg_semantical_equivalence_analyser_test.py
│   │       ├── openai_semantical_equivalence_analyser_test.py
│   │       └── sem_eq_transformer_analyser_test.py
│   └── utils_test/
│       └── utils_test.py
└── utilis_test/
    ├── dataclasses_user_story_test.py
    └── util_functions_test.py
```

## Test Functions

### `computation_of_dependencies_test/order_dependencies_test.py`

| Test | Description |
|---|---|
| `test_order_dependency` | Detects a direct order dependency between user stories |
| `test_negativ_order_dependency` | Confirms absence of order dependency in non-matching stories |
| `test_hierarchical_order_dependency` | Detects order dependency in a hierarchical story chain |
| `test_negativ_hierarchical_order_dependency` | Confirms absence in hierarchical stories with no dependency |

### `preprocessing_piplines_test/template_based_splitter_test.py`

| Test | Description |
|---|---|
| `test_single_target_consonant_entity` | Generates a basic story with a consonant-initial entity (article `"a"`) |
| `test_single_target_vowel_entity` | Generates a basic story with a vowel-initial entity (article `"an"`) |
| `test_multiple_targets_produce_multiple_stories` | Multiple action-entity pairs produce one story each |
| `test_stories_end_with_period` | All generated stories end with a period |
| `test_returns_set_of_strings` | Return types are `set` of `str` for both basic and enriched stories |
| `test_persona_appears_in_story` | The persona string appears in every generated story |
| `test_article_selection` | Parameterised — correct article (`a`/`an`) selected for various entities |
| `test_benefit_targets_produce_enriched_stories` | Providing benefit targets produces enriched stories |
| `test_enriched_stories_contain_so_that` | Enriched stories contain the `"so that"` clause |
| `test_benefit_vowel_article` | Correct article used for vowel-initial benefit entities |
| `test_multiple_benefit_targets_multiply_stories` | 1 basic story × N benefit targets = N enriched stories |
| `test_multiple_targets_and_benefits_cross_product` | M basic stories × N benefit targets = M×N enriched stories |
| `test_no_benefit_targets_returns_empty_enriched` | `None` benefit targets returns an empty enriched set |
| `test_empty_benefit_targets_returns_empty_enriched` | Empty benefit target set returns an empty enriched set |

### `preprocessing_piplines_test/lemmatizing_test/lemmatize_test.py`

| Test | Description |
|---|---|
| `test_lemmatize_single_word` | Lemmatizes a single word to its base form |
| `test_lemmatize_single_word_edge_cases` | Edge cases for single-word lemmatization |
| `test_lemmatize_context_aware_single_words` | Context-sensitive lemmatization of single words |
| `test_lemmatize_context_aware_edge_cases` | Edge cases for context-aware lemmatization |
| `test_lemmatize_sentence_single_sentence` | Lemmatizes all tokens in a single sentence |
| `test_lemmatize_sentence_multiple_sentences` | Lemmatizes tokens across multiple sentences |
| `test_lemmatize_sentence_with_punctuation` | Handles punctuation correctly during lemmatization |
| `test_caching_behavior` | Verifies that repeated calls use the function cache |

### `relationship_analysers_classifier_test/crud_classifier/fasttext_similarity_test.py`

| Test | Description |
|---|---|
| `test_classify_restore` | Classifies "restore" as `CREATE` |
| `test_classify_remove` | Classifies "remove" as `DELETE` |
| `test_classify_modify` | Classifies "modify" as `UPDATE` |
| `test_classify_share` | Classifies "share" as `READ` |
| `test_classify_multi_word_sentence` | Classifies a multi-word phrase correctly |
| `test_classify_returns_tuple` | Return type is `tuple[CrudAction, float]` |
| `test_classify_single_word` | Single-word input is classified correctly |
| `test_classify_case_insensitive` | Classification is case-insensitive |

### `relationship_analysers_classifier_test/crud_classifier/gensim_word2vec_similarity_test.py`

| Test | Description |
|---|---|
| `test_classify_restore` | Classifies "restore" as `CREATE` |
| `test_classify_remove` | Classifies "remove" as `DELETE` |
| `test_classify_modify` | Classifies "modify" as `UPDATE` |
| `test_classify_multi_word_sentence` | Classifies a multi-word phrase correctly |
| `test_classify_returns_tuple` | Return type is `tuple[CrudAction, float]` |
| `test_classify_out_of_vocabulary` | Returns a result for out-of-vocabulary words |
| `test_substantiv` | Classifies a noun-style input correctly |

### `relationship_analysers_classifier_test/crud_classifier/gdwg_crud_classifier_test.py`

| Test | Description |
|---|---|
| `test_classify_create` | Classifies "add" as `CREATE` |
| `test_classify_read` | Classifies "retrieve" as `READ` |
| `test_classify_update` | Classifies "modify" as `UPDATE` |
| `test_classify_delete` | Classifies "remove" as `DELETE` |
| `test_classify_case_insensitive_response` | Uppercase model response is lowercased before comparison |
| `test_classify_unknown_no_separator` | Response without `--` separator returns `UNKNOWN` |
| `test_classify_unknown_unrecognised_crud_type` | Unrecognised CRUD type in response returns `UNKNOWN` |
| `test_classify_unknown_empty_first_part` | Empty first part before `--` returns `UNKNOWN` |
| `test_classify_unknown_empty_second_part` | Empty second part after `--` returns `UNKNOWN` |
| `test_classify_unknown_too_many_separators` | More than one `--` in the response returns `UNKNOWN` |
| `test_classify_api_exception_returns_unknown` | Exception during API call returns `UNKNOWN` with 0.0 confidence |
| `test_classify_returns_tuple` | `classify` always returns a `(CrudAction, float)` tuple |
| `test_init_sets_model_name` | `model_name` is stored as `gdwg_{model}` |
| `test_init_sets_model_name_str` | Raw model name string is stored in `model_name_str` |
| `test_init_sets_context_window` | `context_windows` is `floor(tokens * safety_margin)` |
| `test_init_single_word_flag` | `single_word` flag is set to `True` on init |
| `test_singleton_returns_same_instance` | Two calls with the same class return the identical object |

### `relationship_analysers_classifier_test/crud_classifier/openai_crud_classifier_test.py`

| Test | Description |
|---|---|
| `test_model_name_is_prefixed` | `model_name` is stored with an `openai_` prefix |
| `test_model_name_str_stored` | Raw model name string is stored in `model_name_str` |
| `test_context_window_computed` | `context_windows` is `floor(tokens * safety_margin)` |
| `test_max_batch_size_default` | Default `max_batch_size` is 100 |
| `test_tiktoken_fallback_encoding` | When `encoding_for_model` raises, `cl100k_base` is used |
| `test_classify_create` | Classifies "add" as `CREATE` |
| `test_classify_read` | Classifies "get" as `READ` |
| `test_classify_update` | Classifies "modify" as `UPDATE` |
| `test_classify_delete` | Classifies "remove" as `DELETE` |
| `test_classify_returns_tuple` | Return type is `tuple[CrudAction, float]` |
| `test_classify_confidence_is_float` | Confidence value is always a `float` |
| `test_classify_response_strips_whitespace` | Extra whitespace around the CRUD label is handled |
| `test_classify_response_case_insensitive` | Response is lowercased before comparison |
| `test_classify_unknown_crud_type` | Unrecognised CRUD label returns `UNKNOWN` |
| `test_classify_malformed_response_no_separator` | Response without `--` separator returns `UNKNOWN` |
| `test_classify_malformed_response_empty_parts` | Response with an empty segment around `--` returns `UNKNOWN` |
| `test_classify_api_exception_returns_unknown` | Exception during API call returns `UNKNOWN` with zero confidence |
| `test_classify_api_called_with_correct_model` | Model name string is forwarded to the API |
| `test_classify_temperature_forwarded` | `temperature=0.0` is forwarded to the API |
| `test_classify_top_p_forwarded` | `top_p=0.3` is forwarded to the API |
| `test_singleton_returns_same_instance` | Same class type returns the identical singleton instance |
| `test_reset_removes_instance` | `reset_crud_classifier` removes the instance from the registry |

### `relationship_analysers_classifier_test/relationship_analysers_test/containment_analyser_test/containment_transformer_analyser_test.py`

| Test | Description |
|---|---|
| `test_is_contained` | Unified containment check — true if any containment relation matches |
| `test_includes` | Tests whether word_b includes word_a |
| `test_is_part_of` | Tests whether word_a is part of word_b |
| `test_could_include` | Tests whether word_b could include word_a |
| `test_could_be_part_of` | Tests whether word_a could be part of word_b |

### `relationship_analysers_classifier_test/relationship_analysers_test/containment_analyser_test/gdwg_containment_analyser_test.py`

| Test | Description |
|---|---|
| `test_are_contained_returns_true` | A pair where entity2 is contained in entity1 returns `True` |
| `test_are_contained_returns_false` | A pair where entity2 is not contained in entity1 returns `False` |
| `test_are_contained_multiple_pairs` | Multiple pairs are all processed and returned |
| `test_are_contained_case_insensitive_true` | Mixed-case `True` in the response is treated as `True` |
| `test_compute_relations_delegates` | `compute_relations` returns the same result as `are_contained` |
| `test_are_contained_api_error_returns_error_tuple` | GDWG API exception yields an `error` result per pair |
| `test_are_contained_respects_max_batch_size` | `max_batch_size=1` sends each pair in a separate API call |
| `test_are_contained_reprompts_for_missing_pair` | Missing pairs in the LLM response trigger a reprompt call |
| `test_are_contained_raises_on_single_oversized_pair` | A pair exceeding the context window on its own raises `ValueError` |
| `test_init_context_window_applied_safety_margin` | `context_windows` is `floor(tokens * safety_margin)` |
| `test_init_uses_fallback_encoding_for_unknown_model` | Unknown model name falls back to the `cl100k_base` encoding |

### `relationship_analysers_classifier_test/relationship_analysers_test/containment_analyser_test/openai_containment_analyser_test.py`

| Test | Description |
|---|---|
| `test_are_contained_returns_true` | A pair where entity2 is contained in entity1 returns `True` |
| `test_are_contained_returns_false` | A pair where entity2 is not contained in entity1 returns `False` |
| `test_are_contained_multiple_pairs` | Multiple pairs are all processed and returned |
| `test_are_contained_case_insensitive_true` | Mixed-case `True` in the response is treated as `True` |
| `test_compute_relations_delegates` | `compute_relations` returns the same result as `are_contained` |
| `test_are_contained_api_error_returns_error_tuple` | OpenAI API exception yields an `error` result per pair |
| `test_are_contained_respects_max_batch_size` | `max_batch_size=1` sends each pair in a separate API call |
| `test_are_contained_reprompts_for_missing_pair` | Missing pairs in the LLM response trigger a reprompt call |
| `test_are_contained_empty_set_returns_empty` | Empty input set returns an empty list without calling the API |

### `relationship_analysers_classifier_test/relationship_analysers_test/sem_eq_analyser_test/gdwg_semantical_equivalence_analyser_test.py`

| Test | Description |
|---|---|
| `test_are_contained_returns_true` | A semantically equivalent pair returns `True` |
| `test_are_contained_returns_false` | A non-equivalent pair returns `False` |
| `test_are_contained_multiple_pairs` | All pairs from a multi-pair batch are returned |
| `test_are_contained_case_insensitive_true` | Mixed-case `True` in the response is treated as `True` |
| `test_compute_relations_delegates` | `compute_relations` returns the same result as `are_contained` |
| `test_entity_type_calls_api` | Analyser initialised with `ENTITY` type sends a request without error |
| `test_action_type_calls_api` | Analyser initialised with `ACTION` type sends a request without error |
| `test_are_contained_api_error_returns_error_tuple` | API exception yields an `error` result per pair |
| `test_are_contained_api_error_multiple_pairs_all_returned_as_error` | All pairs in a failing batch receive an `error` result |
| `test_are_contained_respects_max_batch_size` | `max_batch_size=1` triggers one API call per pair |
| `test_are_contained_reprompts_for_missing_pair` | Missing pairs in the LLM response trigger a reprompt call |
| `test_are_contained_empty_set_returns_empty` | Empty input set returns an empty list without calling the API |

### `relationship_analysers_classifier_test/relationship_analysers_test/sem_eq_analyser_test/openai_semantical_equivalence_analyser_test.py`

| Test | Description |
|---|---|
| `test_are_contained_returns_true` | A pair of semantically equivalent entities returns `True` |
| `test_are_contained_returns_false` | A pair of non-equivalent entities returns `False` |
| `test_are_contained_multiple_pairs` | Multiple pairs are all processed and returned |
| `test_are_contained_case_insensitive_true` | Mixed-case `True` in the response is treated as `True` |
| `test_compute_relations_delegates` | `compute_relations` returns the same result as `are_contained` |
| `test_init_with_action_type` | Analyser initialises correctly with `TypeGraphUs.ACTION` |
| `test_init_with_persona_type` | Analyser initialises correctly with `TypeGraphUs.PERSONA` |
| `test_action_typ_used_in_api_call` | When `typ=ACTION` an API call is made and the result is returned |
| `test_are_contained_api_error_returns_error_tuple` | OpenAI API exception yields an `error` result per pair |
| `test_are_contained_respects_max_batch_size` | `max_batch_size=1` sends each pair in a separate API call |
| `test_are_contained_reprompts_for_missing_pair` | Missing pairs in the LLM response trigger a reprompt call |
| `test_are_contained_empty_set_returns_empty` | Empty input set returns an empty list without calling the API |

### `relationship_analysers_classifier_test/relationship_analysers_test/sem_eq_analyser_test/sem_eq_transformer_analyser_test.py`

| Test | Description |
|---|---|
| `test_compute_relations_return_types_and_bounds` | Parameterised — result is `bool` and confidence is in `[0, 1]` |
| `test_compute_relations_result_consistent_with_threshold` | Parameterised — boolean result equals `confidence >= threshold` |
| `test_compute_relations_same_word_returns_false` | Identical child and parent returns `False` |
| `test_compute_relations_empty_child_raises` | Empty child string raises `ValueError` |
| `test_compute_relations_empty_parent_raises` | Empty parent string raises `ValueError` |
| `test_compute_relations_asymmetric` | Both direction confidences are valid floats in `[0, 1]` |

### `relationship_analysers_classifier_test/utils_test/utils_test.py`

| Test | Description |
|---|---|
| `test_clean_element` | Strips and normalises a raw element string |
| `test_extract_triple_valid` | Parses a valid `(A, rel, B)` triple string |
| `test_extract_triple_invalid` | Raises or handles malformed triple strings |
| `test_extract_triple_custom_separator` | Parses triples with a non-default separator |
| `test_extract_triple_elements_valid` | Extracts multiple triples from a multi-line string |
| `test_extract_triple_elements_with_invalid` | Skips invalid lines when extracting triples |
| `test_extract_triple_elements_custom_separators` | Extraction with custom separators |
| `test_extract_triple_elements_empty_string` | Handles empty input |
| `test_extract_triple_elements_only_whitespace` | Handles whitespace-only input |
| `test_llm_output_format` | Parses a typical raw LLM output string |
| `test_requirements_engineering_format` | Parses RE-domain formatted triple output |

### `utilis_test/dataclasses_user_story_test.py`

| Test | Description |
|---|---|
| `test_str` *(Persona, Action, Entity, Trigger, Target, Containment)* | `__str__` returns the expected string representation |
| `test_equality` | Two instances with identical values are equal |
| `test_inequality` / `test_inequality_different_name` | Instances with differing fields are not equal |
| `test_inequality_different_type` | Comparison against a non-dataclass type returns `False` |
| `test_hash_equal_objects` | Equal objects produce the same hash |
| `test_usable_in_set` | Objects can be used in sets with correct deduplication |
| `test_basic_fields_parsed` | `pid`, `story`, and `benefit` are parsed from the raw dict |
| `test_pid_stripped_from_story` | `#G00#`-style PID prefix is removed from the story text |
| `test_goal_extracted` | Benefit clause (`so that ...`) is stripped; only the goal part is kept |
| `test_personas_parsed` | Persona list is correctly populated |
| `test_goal_actions_parsed` | Goal actions are correctly populated |
| `test_goal_entities_parsed` | Goal entities are correctly populated |
| `test_triggers_parsed` | `Trigger` objects are created with correct `src` and `trg` |
| `test_goal_targets_parsed` | `Target` objects are created with correct `src` and `trg` |
| `test_crud_action_parsed` | `GoalActionCrud` string is converted to the correct `CrudAction` enum |
| `test_unknown_crud_on_missing_key` | Missing `GoalActionCrud` key defaults to `CrudAction.UNKNOWN` |
| `test_benefit_actions_and_entities_parsed` | Benefit actions and entities are correctly populated |
| `test_containment_parsed` | `Containment` objects are created for `Contains` entries |
| `test_malformed_trigger_skipped` | Triggers with wrong tuple length are silently skipped |
| `test_malformed_target_skipped` | Targets with wrong tuple length are silently skipped |
| `test_empty_input_returns_defaults` | Empty dict produces a record with all default values |
| `test_action_objects_reused_across_goal_and_benefit` | Action appearing in both goal and benefit is the same object |
| `test_factory_import_single` | `AtomicUserStoryRecord.factory_import` populates all fields correctly |
| `test_factory_import_defaults_on_empty_lists` | Empty `UserStoryRecord` produces default `Persona`, `Action`, `Target` |
| `test_factory_bulk_import` | Bulk import returns one `AtomicUserStoryRecord` per input record |
| `test_factory_direct_import` | `factory_direct_import` parses a raw dict end-to-end |
| `test_factory_bulk_direct_import` | Bulk direct import processes a list of raw dicts |
| `test_crud_action_propagated` | `CrudAction` is propagated correctly through to `AtomicUserStoryRecord` |

### `utilis_test/util_functions_test.py`

| Test | Description |
|---|---|
| `test_extract_goals_from_text` | Strips the benefit clause and returns only the goal part |
| `test_remove_pid_from_text` | Removes the `#G00#`-style PID prefix from a user story string |

## Writing Tests

- Files: `*_test.py`
- Classes: `Test*`