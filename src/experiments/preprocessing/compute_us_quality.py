import json
from pathlib import Path
from utilis.keys_us_part import KeyOfUserStoryPart
from preprocessing_piplines.quality_checks import (
    check_well_formed,
    check_atomicity,
    check_minimality
)


def process_us_quality(data: list[dict]) -> list[tuple[dict, list[str]]]:
    """_summary_

    Args:
        data (list[dict]): import the User Stories data

    Returns:
        list[tuple[dict, list[str]]]: a List of US which do not conform to quality checks along with the failed checks
    """
    result: list[tuple[dict, list[str]]] = []
    for us in data:
        failed_checks = []
        if not check_well_formed(us):
            failed_checks.append("well_formed")
        if not check_atomicity(us, KeyOfUserStoryPart.goal_part):
            failed_checks.append("atomicity_goal_part")
        if not check_minimality(us, KeyOfUserStoryPart.goal_part):
            failed_checks.append("minimality_goal_part")
        
        if failed_checks:
            result.append((us, failed_checks))
            
    return result

current_file = Path(__file__).resolve()
data_path = current_file.parents[1] / "_data" / "original_data"

file: str = input("Enter the filename (without extension) to process User Stories quality: ") 
file = file.strip()
file += ".json" if not file.endswith(".json") else ""

us_data: list[dict] = []
with open(data_path / file, "r", encoding="utf-8") as f:
    temp: str = ""
    for line in f:
        temp += line
    us_data = json.loads(temp)
    
us_quality_issues = process_us_quality(us_data)
print(f"Total User Stories with quality issues: {len(us_quality_issues)}")
for us_record, issues in us_quality_issues:
    print(f"{us_record.get('Text', 'N/A')} - Issues: {issues}")