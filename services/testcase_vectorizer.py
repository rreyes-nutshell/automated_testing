# <<04-JUN-2025:00:05>> – services/testcase_vectorizer.py
# Purpose: Read one or multiple sheets from an Excel file, embed each row as a vector, and store in ChromaDB.

import os
import sys
# <<04-JUN-2025:00:05>> - Ensure project root is in sys.path for utils imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import torch
from sentence_transformers import SentenceTransformer
import chromadb
from utils.logging import debug_log

# ─── ChromaDB SETUP ───────────────────────────────────────────────────────────
chroma_client = chromadb.Client()
testcase_collection = chroma_client.get_or_create_collection("testcase_vectors")

# ─── EMBEDDING MODEL SETUP ─────────────────────────────────────────────────────
# You can replace 'all-MiniLM-L6-v2' with any local text-embedding model.
embed_model = SentenceTransformer('all-MiniLM-L6-v2')

def vectorize_text(text: str) -> list[float]:
    """
    <<03-JUN-2025:23:45>> – Entered vectorize_text
    Generate a normalized (L2-normalized) embedding for the given text.
    """
    raw_emb = embed_model.encode(text)
    tensor = torch.tensor(raw_emb)
    normed = tensor / torch.norm(tensor)
    vector = normed.tolist()
    debug_log("Exited vectorize_text")
    return vector


def index_testcases_from_xlsx(xlsx_path: str, sheet_name: str = None):
    """
    <<03-JUN-2025:23:45>> – Entered index_testcases_from_xlsx
    Read each row from one or multiple sheets of 'xlsx_path', build a text string per test case,
    embed it, and insert into ChromaDB under collection "testcase_vectors".
    If sheet_name is a string, only that sheet is processed.
    If sheet_name is a list, only those sheets are processed.
    If sheet_name is None, all sheets are processed.
    """
    debug_log(f"Indexing test cases from {xlsx_path} (sheet: {sheet_name or 'ALL'})")

    # 1. Load spreadsheet. If sheet_name is None, read all sheets into a dict of DataFrames.
    if sheet_name is None:
        sheets_dict = pd.read_excel(xlsx_path, sheet_name=None)
    elif isinstance(sheet_name, list):
        sheets_dict = {sn: pd.read_excel(xlsx_path, sheet_name=sn) for sn in sheet_name}
    else:
        sheets_dict = {sheet_name: pd.read_excel(xlsx_path, sheet_name=sheet_name)}

    # 2. Iterate over each sheet
    for sn, df in sheets_dict.items():
        debug_log(f"Processing sheet: {sn} (rows: {len(df)})")
        for idx, row in df.iterrows():
            # a) Unique ID: use 'Test ID' if present, else combine sheet name and row index
            raw_id = row.get("Test ID", None)
            if pd.notna(raw_id):
                test_id = str(raw_id).strip()
            else:
                test_id = f"{sn}_row_{idx}"

            # b) Build concatenated text string from relevant columns
            title = str(row.get("Title", "")).strip()
            description = str(row.get("Description", "")).strip()
            expected = str(row.get("Expected Result", "")).strip()
            text = f"{test_id} | {title} | {description} | Expected: {expected}"

            # c) Skip if already in ChromaDB
            existing = testcase_collection.get(ids=[test_id])["ids"]
            if existing:
                continue

            # d) Vectorize the text
            vector = vectorize_text(text)

            # e) Prepare metadata to store
            metadata = {
                "test_id": test_id,
                "sheet": sn,
                "title": title,
                "description": description,
                "expected": expected,
                "source_file": os.path.basename(xlsx_path),
                "row_index": idx,
            }

            # f) Insert into ChromaDB
            testcase_collection.add(
                ids=[test_id],
                embeddings=[vector],
                metadatas=[metadata],
                documents=[text]
            )
    debug_log("Finished indexing test cases from all sheets")
    # <<03-JUN-2025:23:45>> – Exited index_testcases_from_xlsx

if __name__ == "__main__":
    # Example CLI usage. Adjust the filename and sheet_name parameter as needed
    TESTCASE_FILE = "test_cases.xlsx"
    # To process all sheets:
    index_testcases_from_xlsx(TESTCASE_FILE)
    # To process only 'Sheet1' and 'Sheet3', use:
    # index_testcases_from_xlsx(TESTCASE_FILE, sheet_name=['Sheet1', 'Sheet3'])
    # To process a single sheet 'Sheet2', use:
    # index_testcases_from_xlsx(TESTCASE_FILE, sheet_name='Sheet2')
