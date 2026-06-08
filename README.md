# DependencyAnalyseAndSynergyOfUserStories

A Pipline for analysing dependencies using NLP LLMs approaches.

## Python
We are using Python 3.9 and Python 3.14 — these versions have to be available in the scope of the local environments.

## Directories

| Directory | Description |
|---|---|
| `Datasets/` | Raw and annotated user story datasets, elaborated ground truth, and data processing/screening scripts (evaluation scripts). |
| `env_dependencies/` | Requirements files for each virtual environment (default, FastText, Gensim, spaCy, Transformers, LLM Transformers). |
| `src/` | Source code: preprocessing pipelines, dependency computation, relationship analysers/classifiers, prompt configs, and utilities. Furthermore, it contains the experiments conducted in the directiory called `experiments` -- this includes also the answers of the AI models. |
| `tests/` | Unit tests to check the functional correctness of the implementation. It is mirroring the `src/` module structure (expecting the `experiments` directory). |

## It has to be create a .env

The .env has to contain the following core elements:

- MODEL_OPENAI=""
- OPEN_AI_MODEL_CONTEXT_WINDOWS=""
- MODEL_KEY_OPENAI=""
- MODEL_GDWG=""
- GDWG_AI_MODEL_CONTEXT_WINDOWS=""
- MODEL_KEY_GDWG=""
- GDWG_API_URL=""

- TEMPRATURE="0.4"
- TOP_P="0.8"
- MAX_BATCH_SIZE_LLM="250"
- CONTEXT_SAFETY_MARGIN="0.65"

- SPACY_MODEL_NAME="en_core_web_trf"
- SPACY_LEMMATIZER_MODE="rule"
- SPACY_LOOKUPS_DATA="en"
- SPACY_MODEL_LEMMATIZATION="en_core_web_trf"
- SPACY_LEMMATIZATION_MODEL_IS_CUSTOM="False"
- SPACY_LEMMATIZATION_MODEL_CUSTOM_MODE_PATH=""
- SPACY_FUNCTION_CACHE_SIZE="256"

- FASTTEXT_MODEL_NAME="crawl-300d-2M-subword"
- FASTTEXT_MODEL_PATH=D:<USER_PATH>\crawl-300d-2M-subword.bin
- FASTTEXT_SUPERVISED_MODEL_NAME="crawl-300d-2M-subword-supervised"
- FASTTEXT_SUPERVISED_MODEL_PATH=D:<USER_PATH>\crawl-300d-2M-subword.bin
- GENSIM_MODEL_NAME="word2vec-google-news-300"
- GENSIM_MODEL_PATH=D:<USER_PATH>\GoogleNews-vectors-negative300.bin

- TRANSFORMER_MODEL_NAME_FOR_SEMANTIC_SIMILARITY="facebook/bart-large-mnli"
- TRANSFORMER_MODEL_NAME_FOR_CONTAINMENT="facebook/bart-large-mnli"
- TRANSFORMER_MODEL_NAME_FOR_GENERAL="facebook/bart-large-mnli"


## Multiple .venvs

As we use multiple NLP projects and the versioning in Python is not always compatipale, we need multiple `.venv`s and requirements files. 
Each has a corresponding `setup_*.ps1` script. Thus we provide:

- **`requirements_default.txt`**: Default requirements using the newest versions of Python libraries (Python 3.14, `.venv_default`).
- **`requirements_fasttext.txt`**: Adjusted for FastText (Python 3.9, `.venv_fasttext`). Pins `numpy==1.26.4` for C++ compatibility and installs `fasttext-wheel==0.9.2`.
- **`requirements_gensim.txt`**: Adjusted for Gensim word embeddings.
- **`requirements_llm_transformers.txt`**: For LLM-based transformer classification via the OpenAI API (Python 3.14, `.venv_llm_transformers`).
- **`requirements_spacy.txt`**: For the spaCy NLP pipeline (Python 3.9, `.venv_spacy`). 
- **`requirements_transformers.txt`**: For HuggingFace Transformer models (Python 3.14, `.venv_transformers`).

## Setup

Each environment has a dedicated PowerShell setup script that creates the virtual environment, upgrades `pip`, and installs the corresponding requirements file. To set up an environment, run the matching script, e.g.:

```powershell
# Default environment (Python 3.14)
.\setup_default.ps1

# FastText environment (Python 3.9)
.\setup_fasttext_env.ps1

# Gensim environment (Python 3.9)
.\setup_gensim_env.ps1

# spaCy environment (Python 3.9)
.\setup_spacy_env.ps1

# Transformers environment (Python 3.14)
.\setup_transformer_env.ps1

# LLM Transformers environment (Python 3.14)
.\setup_llm_transformer.ps1
```

## Data Sources

- [Raw User Stories](https://data.mendeley.com/datasets/7zbk8zsd8y/1)
- [Annotated User Stories](https://github.com/ace-design/nlp-stories/tree/main)

## Large Language Models

- **OpenAI** (gpt-5.2-2025-12-11)  
- **GDWG Services** [available in-house models](https://docs.hpc.gwdg.de/services/ai-services/chat-ai/models/index.html)

## NLP Models & Directory Layout

All local models live under a top-level `models/` directory  (need to be created):

models/
├── spacy/
│ └── en_core_web_trf-3.8.0-py3-none-any.whl
├── word embeddings
│ └── crawl-300d (FastText)
└ └── Google News (Gensim)


### Installing the spaCy Transformer Model

To power high-quality lemmatization (and full tagging, parsing & NER), we use [<i>spaCy’s</i>](https://spacy.io/) [<i>en_core_web_trf</i>](https://spacy.io/models/en#en_core_web_trf) and [<i>en_core_web_lg</i>](https://spacy.io/models/en#en_core_web_lg) pipeline.
All models can be found on the webpage of [<i>spacy-models</i>](https://github.com/explosion/spacy-models).
[<i>en_core_web_trf</i>](https://huggingface.co/spacy/en_core_web_trf) and [<i>en_core_web_lg</i>](https://huggingface.co/spacy/en_core_web_lg) can also be found on HuggingFace. Furthermore, we are using predefined [lookup-tables](https://github.com/explosion/spacy-lookups-data) so that in the case a model does not find anything we have a fallback.

1. Activate your virtual environment
2. Install spaCy with Transformers support with
    - python -m spacy download en_core_web_lg
    - pip install spacy[transformers]
    - python -m spacy download en_core_web_trf
3. Validate the installation with python -m spacy validate

Alternativly:
1. Activate your virtual environment
2. Install dependency from .whl with
    - PATH_TO_.whl --target=INSTALLATION_PATH_TO_FOLDER
    - e.g. pip install "<ABSOLUTE_PATH_TO_WHEEL>/en_core_web_trf-3.8.0-py3-none-any.whl"     --target="<ABSOLUTE_TARGET_DIR>/nlp_models/spacy"
3 Check for model with e.g. ls <ABSOLUTE_TARGET_DIR>/nlp_models/spacy/en_core_web_trf

### Installing FastText
The easiest way is to install FastText with a specific version.
The command to do is: pip install fasttext-wheel==0.9.2

0. It is refering back to the Visual Studio thus the newest version has to be installed and from there it can compile the c++ dependencies for python

1. Installing a c++ compiler via https://www.msys2.org/ (MinGW) like g++-4.7.2 or higher
    1. Setting the env-Variables
    2. using which gcc
    3. gcc -v
    4. gdb -v

2. Alternativly via:
    1. https://winlibs.com/
    2. Tutorial https://www.youtube.com/watch?v=yTKcqdSGuF0

3. Alternativly:  
    - pip install . 
    - https://fasttext.cc/docs/en/supervised-tutorial.html

5. If c++ errors arise a cross compilation via linux (wsl) is also possible and easy to do

4. Using the tutoril here https://github.com/facebookresearch/fastText

## Submodules

This project considers submodules thus when downloading the project it has to be considered to execute the following:

- git clone --recurse-submodules <URL>

If you have already cloned the project then you can execute the following:

- git submodule update --init --recursive

For updating the submodules late you can:

- git submodule update --recursive --remote