# Excel Sheet Processor

A Python command-line tool to process Excel (`.xlsx`) workbooks with multiple sheets.
For each selected sheet, the tool compares two columns row-wise and writes `0` or `1`
into configurable target columns based on the comparison result.

---

## Features

- Processes **multiple Excel sheets (tabs)** in one workbook
- Sheet-specific rules (`0` or `1` on equality)
- Fully configurable via **command-line arguments**
- Configurable:
  - input / output file
  - start row
  - columns to compare
  - target columns to modify
- Optional default rule for non-listed sheets
- Robust value normalization (trim / case-insensitive)
- Progress bars using `tqdm`
- Optional processing delays (per row / per sheet)

---

## Requirements

- Python **3.10+**
- Dependencies:
  ```bash
  pip install openpyxl tqdm
  ```

## Processing Logic

For each processed sheet and each row (starting at `START_ROW`):

- If **COMPARE_COL_1 == COMPARE_COL_2**
  → write `equal_value` (`0` or `1`)
- Otherwise
  → write the **opposite value**
- Values are written to all configured **target columns**
- Empty rows can optionally be skipped

---

## Installation

Install required dependencies:

```bash
pip install openpyxl tqdm
```
## Usage

### Run with defaults defined in the script

```bash
python excel_sheet_processor.py
```

### Specify input and output files

```bash
python excel_sheet_processor.py -i g03.xlsx -o output.xlsx
```

### Specify input and output files
```bash
python excel_sheet_processor.py \
  -i g03.xlsx \
  -o output.xlsx \
  --start-row 2 \
  --compare-cols A B \
  --targets D E F
```

### Define sheet-specific rules
```bash
python excel_sheet_processor.py \
  -i g03.xlsx \
  -o output.xlsx \
  --sheet-rules '{"HS4ConOfE":0,"HS4SemOfP":1}'
```

with the format:

  ```bash
  {
  "SheetName": 0,
  "AnotherSheet": 1
}
```


### Use a default rule for all other sheets
```bash
python excel_sheet_processor.py \
  -i g03.xlsx \
  -o output.xlsx \
  --use-default-for-other-sheets \
  --default-equal 1
```

 ## Command-Line Options

| Option | Description |
|------|-------------|
| `-i`, `--input` | Input `.xlsx` file |
| `-o`, `--output` | Output `.xlsx` file |
| `--start-row` | First row to process |
| `--compare-cols` | Two columns to compare |
| `--targets` | Columns to write values into |
| `--sheet-rules` | JSON mapping sheet → equal value |
| `--use-default-for-other-sheets` | Enable default rule |
| `--default-equal` | Default equal value (`0` or `1`) |
| `--trim` | Trim whitespace before comparing |
| `--case-insensitive` | Ignore character case |
| `--no-skip-empty` | Do not skip empty rows |

---

## Notes

- Only the configured **target columns** are modified
- Each changed cell is counted as a change
- Designed for **batch processing**
- Safe to re-run on the same file (idempotent output)