# CRUD Classifier

This module classifies a verb or short operation phrase extracted from a user story into one of the four CRUD categories: **Create**, **Read**, **Update**, or **Delete** (with an `Unknown` fallback).

## Overview

The classifier is built around a common abstract interface (`InterfaceCrudClassifier`) and provides multiple backends suited to different environments:

| Class | Backend | Environment |
|---|---|---|
| `CrudAnalyserOpenAI` | OpenAI API | `.venv_default` / `.venv_llm_transformers` |
| `CrudAnalyserGdwg` | GWDG in-house LLM API | `.venv_default` / `.venv_llm_transformers` |
| `FastTextCrudAnalyserClassifier` | FastText word embeddings | `.venv_fasttext` |
| `GensimWord2VecCRUDClassifier` | Google Word2Vec via Gensim | `.venv_gensim` |

All classifiers return a `tuple[CrudAction, float | None]` — the predicted CRUD label and an optional confidence score.

## Structure
crud_classifier<br>
├── interface_crud_classifier.py # Abstract base class (Singleton pattern)<br>
├── crud_actions.py # CrudAction enum (CREATE, READ, UPDATE, DELETE, UNKNOWN)<br>
├── openai_crud_classifier.py # LLM classifier via OpenAI API<br>
├── gdwg_crud_classifier.py # LLM classifier via GWDG API <br>
├── fasttext_analyser_similarity.py # Centroid-based classifier using FastText <br>
├── gensim_word2vec_similarity.py # Centroid-based classifier using Word2Vec <br>
├── load_crud_mappings.py # Loads CRUD keyword mappings from JSON
└── data/ <br>
└── crud_mappings_30.json # Bag-of-words keyword lists per CRUD class <br>

## CRUD Mappings

The `data/crud_mappings_*.json` files define a bag-of-words per CRUD class used by the embedding-based classifiers to build class centroids. The `bag_of_words_size` parameter controls which mapping file is loaded.