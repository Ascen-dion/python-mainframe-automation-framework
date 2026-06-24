def extract_field(screen_text: str, row: int, col: int, length: int) -> str:
    """Extracts text from a specific Row/Col coordinate on the 24x80 grid."""
    lines = screen_text.split('\n')
    if not lines or row < 1 or row > len(lines):
        return ""
    
    target_line = lines[row - 1].ljust(80)
    start_idx = col - 1
    return target_line[start_idx : start_idx + length].strip()

def scrape_screen_data(screen_text: str, or_screen_node: dict) -> dict:
    """Iterates through the Object Repository mapping and extracts all fields."""
    extracted_data = {}
    for field_name, coords in or_screen_node.items():
        extracted_data[field_name] = extract_field(
            screen_text, 
            row=coords["row"], 
            col=coords["col"], 
            length=coords["length"]
        )
    return extracted_data