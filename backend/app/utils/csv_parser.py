import csv
import io
from typing import List, Dict, Any, Tuple

GERMAN_HEADER_MAP = {
    "werksnummer": "Plant Code",
    "brennstofftyp": "Fuel Type",
    "menge": "Quantity",
    "einheit": "Unit",
    "lieferant": "Vendor",
    "rechnungsdatum": "Invoice Date",
    "kostenstelle": "Cost Center",
    "währung": "Currency",
    "belegnummer": "Invoice Number"
}

def parse_csv_bytes(file_bytes: bytes) -> Tuple[List[Dict[str, str]], List[str]]:
    """
    Parses CSV contents from raw bytes.
    Handles UTF-8 and Latin-1, standard separators, and German headers.
    Returns: (parsed_rows, original_headers)
    """
    # Try decoding
    text = ""
    for encoding in ["utf-8-sig", "utf-8", "latin1"]:
        try:
            text = file_bytes.decode(encoding)
            break
        except UnicodeDecodeError:
            continue
            
    if not text:
        raise ValueError("Unsupported file encoding. Please upload UTF-8 or Latin-1 files.")
        
    # Detect separator (comma vs semicolon)
    sample = text[:1000]
    separator = ";" if ";" in sample and sample.count(";") > sample.count(",") else ","
    
    f = io.StringIO(text)
    reader = csv.reader(f, delimiter=separator)
    
    # Read headers
    try:
        headers = next(reader)
    except StopIteration:
        return [], []
        
    headers = [h.strip() for h in headers]
    original_headers = headers.copy()
    
    # Normalize headers
    normalized_headers = []
    for h in headers:
        h_lower = h.lower()
        if h_lower in GERMAN_HEADER_MAP:
            normalized_headers.append(GERMAN_HEADER_MAP[h_lower])
        else:
            normalized_headers.append(h)
            
    rows = []
    for row in reader:
        if not row or all(cell.strip() == "" for cell in row):
            continue  # skip blank lines
            
        # Pad row if columns are shorter than headers
        if len(row) < len(normalized_headers):
            row.extend([""] * (len(normalized_headers) - len(row)))
            
        row_dict = {}
        for idx, header in enumerate(normalized_headers):
            if idx < len(row):
                row_dict[header] = row[idx].strip()
            else:
                row_dict[header] = ""
        rows.append(row_dict)
        
    return rows, original_headers
