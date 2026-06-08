# Containment Analyser - Transformer Approach

Analyzes semantic containment relationships between words using NLI models.

## Quick Start

```python
from transformer_containment_approach import ContainmentAnalyserTransformer

analyser = ContainmentAnalyserTransformer()
is_contained, confidence = analyser.is_contained("password", "user", threshold=0.7)
```

## Model Configuration

Set the model via environment variable recoding to one of the following models


## Available Models

| Model | URL |
|-------|-----|
| `cross-encoder/nli-deberta-large` | https://huggingface.co/cross-encoder/nli-deberta-large |
| `microsoft/deberta-large-mnli` | https://huggingface.co/microsoft/deberta-large-mnli |
| `facebook/bart-large-mnli` | https://huggingface.co/facebook/bart-large-mnli |
| `roberta-large-mnli` | https://huggingface.co/roberta-large-mnli |
| `facebook/bart-base-mnli` (currently used) | https://huggingface.co/facebook/bart-base-mnli |

## Methods

- `is_contained(word_a, word_b, threshold)` — Unified check (True if ANY relationship matches)
- `includes(word_a, word_b, threshold)` — Does word_b include word_a?
- `is_part_of(word_a, word_b, threshold)` — Is word_a part of word_b?
- `could_include(word_a, word_b, threshold)` — Could word_b include word_a?
- `could_be_part_of(word_a, word_b, threshold)` — Could word_a be part of word_b?
