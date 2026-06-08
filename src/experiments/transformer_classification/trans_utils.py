from pathlib import Path

def save_results_to_csv(file_path: Path, results: list[tuple], headers: str) -> None:
    """Save classification results to a CSV file."""
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(headers)
        for r in results:
            f.write(f'{r[0]}|{r[1]}|{r[2]}|{r[3]}\n')
            
def print_or_log(message: str, file_name: str, file_path: Path, log: bool = False) -> None:
    """Print message to console and append to log file."""
    if not log: 
        print(message)
    else: 
        log_file = file_path / f"{file_name}_log.txt"
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(message + "\n")

def get_yes_no_input(prompt: str, default: bool = False) -> bool:
    """Get yes/no input from user with default value."""
    default_str = "yes" if default else "no"
    user_input = input(f"{prompt} ({default_str}): ").strip().lower()
    
    if user_input in ("y", "yes", "1", "true"):
        return True
    elif user_input in ("n", "no", "0", "false"):
        return False
    elif user_input == "":
        return default
    else:
        return default