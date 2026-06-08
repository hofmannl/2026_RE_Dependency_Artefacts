# Semantical Equivalence Analyser

Analyses whether two elements extracted from user stories are semantically equivalent (i.e. interchangeable in meaning). Supports entities, actions, and personas.

The LLM redundancy checks are done with the implementation presented in https://link.springer.com/chapter/10.1007/978-3-031-88531-0_18

## Quick Start

```python
from transformer_equivalence_approach import SemanticEquivalenceAnalyserTransformer
from utilis.annotation_graph_components import TypeGraphUs

analyser = SemanticEquivalenceAnalyserTransformer(typ=TypeGraphUs.ENTITY)
is_equivalent, confidence = analyser.is_semantical_equivalent("administrator", "admin", threshold=0.7)
```

## Available Backends

| Class | Backend | Environment |
|---|---|---|
| `SemanticEquivalenceAnalyserTransformer` | HuggingFace zero-shot NLI | `.venv_transformers` |
| `SemanticEquivalenceAnalyserOpenAI` | OpenAI API | `.venv_llm_transformers` |
| `SemanticEquivalenceAnalyserGdwg` | GWDG in-house LLM API | `.venv_llm_transformers` |

All backends implement `RelationResolver` and return `tuple[bool, float]` — the equivalence decision and confidence score.

## Element Types

The transformer approach supports three element types via `TypeGraphUs`:

| Type | Description |
|---|---|
| `TypeGraphUs.ENTITY` | Nouns / domain concepts (e.g. `"user"`, `"admin"`) |
| `TypeGraphUs.ACTION` | Verbs / operations (e.g. `"delete"`, `"remove"`) |
| `TypeGraphUs.PERSONA` | Roles (e.g. `"manager"`, `"administrator"`) |

## Transformer Model Configuration

Set the model via the environment variable `TRANSFORMER_MODEL_NAME`. Supported models:

| Model | URL |
|---|---|
| `facebook/bart-large-mnli` (default) | https://huggingface.co/facebook/bart-large-mnli |
| `cross-encoder/nli-deberta-large` | https://huggingface.co/cross-encoder/nli-deberta-large |
| `microsoft/deberta-large-mnli` | https://huggingface.co/microsoft/deberta-large-mnli |
| `roberta-large-mnli` | https://huggingface.co/roberta-large-mnli |
| `facebook/bart-base-mnli` | https://huggingface.co/facebook/bart-base-mnli |

## Methods

- `is_semantical_equivalent(first_element, second_element, threshold)` — Returns `(bool, float)` indicating whether the two elements are semantically equivalent.
- `compute_relations(child, parent, threshold)` — Unified interface inherited from `RelationResolver`.