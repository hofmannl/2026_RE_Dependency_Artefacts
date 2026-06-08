# User Story Data Processing Scripts

This directory contains Python scripts for converting and analyzing user story JSON data into various CSV formats.

## Prerequisites

- Python 3.x
- Virtual environment (`.venv`) with required packages:
  - pandas
  - openpyxl (optional, for Excel support)

## Setup

### 1. Activate the Virtual Environment

**Windows (PowerShell):**
```powershell
.\.venv\Scripts\Activate.ps1
```

**Windows (Command Prompt):**
```cmd
.venv\Scripts\activate.bat
```

**Linux/macOS:**
```bash
source .venv/bin/activate
```

### 2. Install Dependencies (if needed)

```bash
pip install pandas openpyxl
```

## Scripts Overview

### 1. `json_to_csv_converter.py`
Converts JSON user story data to a single-row CSV format with multiple Goal and Benefit columns.

**Output Format:**
- One row per user story
- Columns: `User Story Text | Persona | Goal Activity | Goal Entity | Goal Activity 2 | Goal Entity 2 | ... | Benefit Activity | Benefit Entity | ...`
- Delimiter: `|` (pipe)

**Usage:**
```bash
python json_to_csv_converter.py <input_json_file> [output_csv_file]
```

**Example:**
```bash
python json_to_csv_converter.py "../elaborated_ground_truth/datasets/annotated/g03_baseline.json" "../g03_baseline_converted.csv"
```

**Output:** 57 rows (one per unique user story)

---

### 2. `json_to_csv_split_edges.py`
Converts JSON user story data to a split-edge CSV format with one row per target edge and sequential IDs.

**Output Format:**
- One row per target edge
- Columns: `User Story Text | ID | Persona | Activity | Entity | Type`
- Delimiter: `|` (pipe)
- Type: Goal or Benefit classification

**Usage:**
```bash
python json_to_csv_split_edges.py <input_json_file> [output_csv_file]
```

**Example:**
```bash
python json_to_csv_split_edges.py "../elaborated_ground_truth/datasets/annotated/g03_baseline.json" "../g03_baseline_split_edges.csv"
```

**Output:** 173 rows (one per target edge)

---

### 3. `extract_goal_actions.py`
Extracts only Goal actions from user stories.

**Output Format:**
- One row per unique goal action per story
- Columns: `User Story Text | Action`
- Delimiter: `|` (pipe)
- Text: Cleaned of "so that" clause

**Usage:**
```bash
python extract_goal_actions.py <input_json_file> [output_csv_file]
```

**Example:**
```bash
python extract_goal_actions.py "../elaborated_ground_truth/datasets/annotated/g03_baseline.json" "../g03_baseline_goal_actions.csv"
```

**Output:** 62 rows (one per unique goal action)

---

### 4. `extract_goal_benefit_parts.py` (Optimized)
Extracts relevant Goal or Benefit parts based on edge type, with optimized output.

**Output Format:**
- One row per edge
- Columns: `User Story Part | Activity | Entity | Type`
- Delimiter: `|` (pipe)
- For Goals: Shows "I want to..." part
- For Benefits: Shows "I can..." part

**Usage:**
```bash
python extract_goal_benefit_parts.py <input_json_file> [output_csv_file]
```

**Example:**
```bash
python extract_goal_benefit_parts.py "../elaborated_ground_truth/datasets/annotated/g03_baseline.json" "../g03_baseline_goal_benefit_parts.csv"
```

**Output:** 168 rows (one per edge, split by Goal/Benefit)

---

### 5. `extract_persona_pairs.py`
Extracts all possible pairs between personas from user stories with lemmatization.

**Output Format:**
- One row per persona pair (all combinations)
- Columns: `Persona 1|Persona 2`
- Delimiter: `|` (pipe)
- Lemmatized and lowercase personas

**Usage:**
```bash
python extract_persona_pairs.py <input_json_file> [output_csv_file]
```

**Example:**
```bash
python extract_persona_pairs.py "../elaborated_ground_truth/datasets/annotated/g03_baseline.json" "../g03_persona_pairs.csv"
```

---

### 6. `extract_goal_action_pairs.py`
Extracts all goal action pairs from user stories with lemmatization.

**Output Format:**
- One row per goal action
- Columns: `Goal Action`
- Delimiter: `|` (pipe)
- Lemmatized and lowercase actions
- Filtered to Primary Actions only

**Usage:**
```bash
python extract_goal_action_pairs.py <input_json_file> [output_csv_file]
```

**Example:**
```bash
python extract_goal_action_pairs.py "../elaborated_ground_truth/datasets/annotated/g03_baseline.json" "../g03_goal_action_pairs.csv"
```

---

### 7. `extract_goal_entities.py`
Extracts all goal entity pairs from user stories with lemmatization.

**Output Format:**
- One row per goal entity
- Columns: `Goal Entity`
- Delimiter: `|` (pipe)
- Lemmatized and lowercase entities
- Filtered to Primary Entities only

**Usage:**
```bash
python extract_goal_entities.py <input_json_file> [output_csv_file]
```

**Example:**
```bash
python extract_goal_entities.py "../elaborated_ground_truth/datasets/annotated/g03_baseline.json" "../g03_goal_entities.csv"
```

---

### 8. `extract_goal_entities_pairs.py` (Pairwise)
Extracts all pairwise combinations of goal entities from user stories.

**Output Format:**
- One row per unique entity pair
- Columns: `Entity 1|Entity 2`
- Delimiter: `|` (pipe)
- All unique combinations of goal entities
- Lemmatized and lowercase

**Usage:**
```bash
python extract_goal_entities_pairs.py <input_json_file> [output_csv_file]
```

**Example:**
```bash
python extract_goal_entities_pairs.py "../elaborated_ground_truth/datasets/annotated/g03_baseline.json" "../g03_goal_entities_pairs.csv"
```

---

### 9. `extract_unique_persona_pairs.py`
Extracts all **unique** persona pairs (avoiding duplicates like A|B and B|A).

**Output Format:**
- One row per unique persona pair
- Columns: `Persona 1|Persona 2`
- Delimiter: `|` (pipe)
- Each pair appears only once (canonical order)
- Lemmatized and lowercase personas

**Usage:**
```bash
python extract_unique_persona_pairs.py <input_json_file> [output_csv_file]
```

**Example:**
```bash
python extract_unique_persona_pairs.py "../elaborated_ground_truth/datasets/annotated/g03_baseline.json" "../g03_unique_persona_pairs.csv"
```

---

### 10. `extract_unique_entity_pairs.py`
Extracts all **unique** entity pairs from goal part (avoiding duplicates).

**Output Format:**
- One row per unique entity pair
- Columns: `Entity 1|Entity 2`
- Delimiter: `|` (pipe)
- Each pair appears only once (canonical order)
- Lemmatized and lowercase entities
- Filtered to Primary Entities only

**Usage:**
```bash
python extract_unique_entity_pairs.py <input_json_file> [output_csv_file]
```

**Example:**
```bash
python extract_unique_entity_pairs.py "../elaborated_ground_truth/datasets/annotated/g03_baseline.json" "../g03_unique_entity_pairs.csv"
```

---

### 11. `extract_unique_action_pairs.py`
Extracts all **unique** action pairs from goal part (avoiding duplicates).

**Output Format:**
- One row per unique action pair
- Columns: `Action 1|Action 2`
- Delimiter: `|` (pipe)
- Each pair appears only once (canonical order)
- Lemmatized and lowercase actions
- Filtered to Primary Actions only

**Usage:**
```bash
python extract_unique_action_pairs.py <input_json_file> [output_csv_file]
```

**Example:**
```bash
python extract_unique_action_pairs.py "../elaborated_ground_truth/datasets/annotated/g03_baseline.json" "../g03_unique_action_pairs.csv"
```

---

## Lemmatization & NLP Processing

Scripts 5-11 use **spaCy** for advanced NLP processing:
- **Lemmatization**: Words are reduced to their base form (e.g., "running" → "run")
- **Lowercase Normalization**: All text is converted to lowercase for consistency
- **Dictionary Caching**: Results are cached to improve performance
- **spaCy Lookups**: Pre-built lemmatization tables for better accuracy

**Requirements:**
- spaCy with English model (`en_core_web_trf`)
- Automatically downloaded on first run if missing

---

## Complete Workflow Example

```powershell
# 1. Activate virtual environment
.\.venv\Scripts\Activate.ps1

# 2. Run basic conversion scripts
python json_to_csv_converter.py "../elaborated_ground_truth/datasets/annotated/g03_baseline.json" "../g03_baseline_converted.csv"

python json_to_csv_split_edges.py "../elaborated_ground_truth/datasets/annotated/g03_baseline.json" "../g03_baseline_split_edges.csv"

python extract_goal_actions.py "../elaborated_ground_truth/datasets/annotated/g03_baseline.json" "../g03_baseline_goal_actions.csv"

python extract_goal_benefit_parts.py "../elaborated_ground_truth/datasets/annotated/g03_baseline.json" "../g03_baseline_goal_benefit_parts.csv"

# 3. Run advanced NLP scripts (with lemmatization)
python extract_persona_pairs.py "../elaborated_ground_truth/datasets/annotated/g03_baseline.json" "../g03_persona_pairs.csv"

python extract_goal_action_pairs.py "../elaborated_ground_truth/datasets/annotated/g03_baseline.json" "../g03_goal_action_pairs.csv"

python extract_goal_entities.py "../elaborated_ground_truth/datasets/annotated/g03_baseline.json" "../g03_goal_entities.csv"

python extract_goal_entities_pairs.py "../elaborated_ground_truth/datasets/annotated/g03_baseline.json" "../g03_goal_entities_pairs.csv"

# 4. Run unique pair extraction scripts (no duplicates)
python extract_unique_persona_pairs.py "../elaborated_ground_truth/datasets/annotated/g03_baseline.json" "../g03_unique_persona_pairs.csv"

python extract_unique_entity_pairs.py "../elaborated_ground_truth/datasets/annotated/g03_baseline.json" "../g03_unique_entity_pairs.csv"

python extract_unique_action_pairs.py "../elaborated_ground_truth/datasets/annotated/g03_baseline.json" "../g03_unique_action_pairs.csv"
```

---

## Input File Format

The input JSON file should have the following structure:

```json
[
  {
    "PID": "#G03#",
    "Text": "#G03# As a Public User, I want to Search for Information, so that I can obtain publicly available information...",
    "Persona": ["Public User"],
    "Action": {
      "Primary Action": ["Search"],
      "Secondary Action": ["obtain"]
    },
    "Entity": {
      "Primary Entity": ["Information"],
      "Secondary Entity": ["publicly available information"]
    },
    "Targets": [
      ["Search", "Information"],
      ["obtain", "publicly available information"]
    ]
  }
]
```

## Classification Rules

- **Goal Edge**: Action in Primary Actions AND Entity in Primary Entities
- **Benefit Edge**: Action in Secondary Actions AND Entity in Secondary Entities
- **Fallback**: If unclear, defaults to Goal

## Output Files

All output CSV files:
- Use `|` (pipe) as delimiter
- Encoded in UTF-8
- Can be opened in Excel, Google Sheets, or any text editor

## Troubleshooting

### ModuleNotFoundError: No module named 'pandas'
Install pandas:
```bash
pip install pandas
```

### Permission Denied (on .ps1 file)
Enable PowerShell script execution:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Path Issues
Ensure you're running the scripts from the `scripts4dataanalyse` directory:
```powershell
cd d:\_Projects\_myProjects\dependencyanalyseandsynergyofuserstories\Datasets\scripts4dataanalyse
```

## Notes

- All scripts skip empty stories
- The PID prefix (#G###) is automatically removed from text
- Duplicate actions within a story are handled (deduplicated where applicable)
- Default output filename: `input_file.replace('.json', '_suffix.csv')`

