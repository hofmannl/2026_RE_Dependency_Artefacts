import json
import os

def load_crud_mappings(file_path: str = os.path.dirname(os.path.abspath(__file__)), sub_path: str = "data", file_name: str = "crud_mappings") -> tuple[dict, dict, dict, dict]:
    """Load CRUD mappings from a JSON file."""
    try:
        if not file_name.endswith(".json"):
            file_name += ".json"
        whole_file_name = os.path.join(file_path, sub_path, file_name)
        with open(whole_file_name, 'r') as f:
            mappings = json.load(f)
        whole_file_name = None 
        return mappings
    except Exception as e:
        return {}