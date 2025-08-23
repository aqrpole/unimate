import os
import pdfplumber
import json
from typing import List, Dict, Optional
import re

# Configuration
DATA_FOLDER = "/home/unimate/unimate/data"
CHUNK_SIZE = 1000  # characters
HEADING_PATTERN = r"^(#+|\b(?:Chapter|Section)\b|\d+\.\d+)\s+(.+)$"

def extract_heading(text: str) -> Optional[str]:
    """Extracts heading from text if matches pattern"""
    match = re.search(HEADING_PATTERN, text.strip(), re.IGNORECASE)
    return match.group(2) if match else None

def process_pdf(file_path: str) -> List[Dict]:
    """Process a single PDF file into chunks with metadata"""
    chunks = []
    try:
        with pdfplumber.open(file_path) as pdf:
            for page_num, page in enumerate(pdf.pages, start=1):
                text = page.extract_text()
                if not text:
                    continue
                
                # Extract potential heading from first lines
                first_lines = "\n".join(text.split("\n")[:3])
                heading = extract_heading(first_lines)
                
                # Split into chunks
                for i in range(0, len(text), CHUNK_SIZE):
                    chunk = text[i:i+CHUNK_SIZE]
                    chunks.append({
                        "doc_id": os.path.basename(file_path),
                        "chunk_text": chunk,
                        "page_number": page_num,
                        "heading": heading if i == 0 else None
                    })
    except Exception as e:
        print(f"Error processing {file_path}: {str(e)}")
    
    return chunks

def save_to_json(data: List[Dict], filename: str):
    """Save processed data to JSON file"""
    output_path = os.path.join(DATA_FOLDER, f"{os.path.splitext(filename)[0]}_processed.json")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    print(f"Saved processed data to {output_path}")

def process_all_pdfs():
    """Process all PDFs in the data folder"""
    if not os.path.exists(DATA_FOLDER):
        print(f"Error: Data folder '{DATA_FOLDER}' not found")
        return []
    
    pdf_files = [f for f in os.listdir(DATA_FOLDER) if f.lower().endswith('.pdf')]
    if not pdf_files:
        print(f"No PDF files found in '{DATA_FOLDER}'")
        return []
    
    all_results = []
    for pdf_file in pdf_files:
        file_path = os.path.join(DATA_FOLDER, pdf_file)
        chunks = process_pdf(file_path)
        if chunks:
            save_to_json(chunks, pdf_file)
            all_results.append({
                "filename": pdf_file,
                "chunks": chunks,
                "total_pages": chunks[-1]["page_number"] if chunks else 0
            })
    
    # This would be the return value if used as a function
    # return all_results
    
    # For demonstration, we'll print and comment the return structure
    print("\nProcessing complete. Example return structure:")
    print("""[
    {
        "filename": "example.pdf",
        "chunks": [
            {
                "doc_id": "example.pdf",
                "chunk_text": "Lorem ipsum...",
                "page_number": 1,
                "heading": "Introduction"
            },
            # ... more chunks
        ],
        "total_pages": 42
    }
    # ... more files
]""")

if __name__ == "__main__":
    process_all_pdfs()