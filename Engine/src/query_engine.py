import os
os.environ["HF_HOME"] = "/cs/ep/110/HUJI-project/hf_cache"
os.environ["TRANSFORMERS_CACHE"] = "/cs/ep/110/HUJI-project/hf_cache"
os.environ["HF_DATASETS_CACHE"] = "/cs/ep/110/HUJI-project/hf_cache"
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

import sys
import re
import faiss
import json
import numpy as np
import torch
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
from Engine.src.constants import *
import ctypes


QUERY_ITEM_MAPPING = {
    "sector": ["Item_1"],
    "total_net_sales": ["Item_8"],
    "net_income": ["Item_8"],
    "eps": ["Item_8"],
    "operating_income": ["Item_8"],
    "gross_profit": ["Item_7", "Item_8"],
    "cash_flow_operating_activities": ["Item_8"],
    "capital_expenditures": ["Item_7"],
    "total_assets": ["Item_8"],
    "total_liabilities": ["Item_8"],
    "sales_and_marketing_expense": ["Item_7", "Item_8"],
    "sga_expense": ["Item_8"],
    "stock_issuance": ["Item_8"],
    "stock_repurchases": ["Item_5", "Item_8"],
    "fiscal_year_end": ["Item_1", "Item_8"],
    "operating_expenses": ["Item_7", "Item_8"],
    "dividends_paid": ["Item_7", "Item_8"],
    "accounts_receivable": ["Item_8"],
    "shareholder_equity": ["Item_5", "Item_6", "Item_7", "Item_8"],
    "research_and_development_expense": ["Item_7", "Item_8"],
    "research_and_development_investment": ["Item_7", "Item_8"],
    "foreign_revenue": ["Item_8"],
    "revenue_streams": ["Item_1", "Item_7", "Item_8"], # literal questions fields
    "customer_base": ["Item_1"],
    "competitive_landscape": ["Item_1"],
    "growth_strategy": ["Item_1", "Item_7"],
    "highlighted_risks": ["Item_1"],
    "regulatory_challenges": ["Item_1", "Item_3"],
    "ebitda_margin": ["Item_7", "Item_8"],
    "operating_expense_commentary": ["Item_7", "Item_8"],
    "valuation_commentary": ["Item_7", "Item_8"],
    "capital_expenditures_projects": ["Item_7", "Item_8"],
    "dividend_and_buyback_policy": ["Item_5", "Item_7"],
    "working_capital_efficiency": ["Item_8"],
    "management_changes": ["Item_10"],
    "supply_chain_disruptions": ["Item_1"],
    "esg_initiatives": ["Item_1"],
    "esg_controversies": ["Item_1", "Item_3"],
    "governance_structure": ["Item_10"],
    "debt_sustainability_commentary": ["Item_1", "Item_7", "Item_8"],
    "debt_refinancing_activity": ["Item_7", "Item_8"],
    "technology_impact_on_operations": ["Item_1", "Item_7"],
    "emerging_tech_investments": ["Item_1"],
    "intellectual_property_assets": ["Item_1"],
    "research_and_development_commentary": ["Item_7", "Item_8"],
    "brand_positioning": ["Item_1"],
    "rebranding_or_marketing_shift": ["Item_1", "Item_7"],
    "macroeconomic_sensitivity": ["Item_1", "Item_7"],
    "geopolitical_and_economic_impacts": ["Item_1", "Item_7"],
    "forward_looking_statement": ["Item_7"]
}

# ----------------------------
# Helper Functions for Windows Paths
# ----------------------------
def get_short_path(long_path):
    buffer = ctypes.create_unicode_buffer(260)  # MAX_PATH
    result = ctypes.windll.kernel32.GetShortPathNameW(long_path, buffer, 260)
    if result:
        return buffer.value
    return long_path


# ----------------------------
# Helper Functions for Passage Augmentation
# ----------------------------
def extract_passage_number(filename):
    """
    Extracts the passage number from a filename like 'passage_230.txt'.
    Returns an integer passage number, or None if not found.
    """
    match = re.search(r'passage_(\d+)\.txt', filename)
    if match:
        return int(match.group(1))
    return None


def read_passage_text(passage_filepath):
    """
    Reads and returns the text content of a passage file.
    If the file does not exist, returns an empty string.
    """
    if os.path.exists(passage_filepath):
        with open(passage_filepath, 'r', encoding='utf-8') as f:
            return f.read().strip()
    return ""


# ----------------------------
# FAISS Index and Retrieval Functions
# ----------------------------
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from constants import HUGGINGFACE_TOKEN

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"


def load_index(index_path, metadata_path):
    """
    Loads the FAISS index and metadata for a specific PDF item.
    """
    index = faiss.read_index(index_path)
    metadata = np.load(metadata_path, allow_pickle=True)
    return index, metadata


def encode_query(query, model):
    """
    Encodes a query into a dense embedding using SentenceTransformer.
    Returns a NumPy array with shape (1, embedding_dimension).
    """
    embedding = model.encode(query, show_progress_bar=False)
    return np.array(embedding).reshape(1, -1)


def retrieve_answers_from_pdf(query, index, metadata, model, top_k=30):
    """
    Retrieves the top-k most relevant passages for a given query from a specific PDF index.
    """
    query_embedding = encode_query(query, model)
    distances, indices = index.search(query_embedding, top_k)

    results = []
    for idx, score in zip(indices[0], distances[0]):
        if idx < len(metadata):
            results.append({
                "score": float(score),  # Ensure it's serializable
                "document": metadata[idx]["document"],
                "file": metadata[idx]["file"],
                "text": metadata[idx]["text"]
            })
    return results


# ----------------------------
# Combined Retrieval and Augmentation Function
# ----------------------------
def query_all_pdfs(query, index_base_dir, metadata_base_dir, model,
                   output_query_dir, passages_root_dir, top_k=10, relevant_items=None):
    """
    Iterates over all document subfolders and, for each document, only processes the item indices
    whose names contain one of the provided substrings in `relevant_items` (if given).
    For each retrieved answer, augment it by adding two adjacent passages before and after
    from the original split passages.
    The final results (with augmented answers) are saved to JSON files under 'output_query_dir'.
    """
    os.makedirs(output_query_dir, exist_ok=True)
    pdf_results = []

    # Iterate over document subfolders in the index base directory.
    for doc_folder in tqdm(os.listdir(index_base_dir), desc="Processing documents"):
        doc_index_path = os.path.join(index_base_dir, doc_folder)
        if not os.path.isdir(doc_index_path):
            continue
        # Corresponding metadata directory for this document.
        doc_metadata_path = os.path.join(metadata_base_dir, doc_folder)

        for index_file in os.listdir(doc_index_path):
            if index_file.endswith(".faiss"):
                item_name = os.path.splitext(index_file)[0]

                # Extract just "Item_X"
                match = re.search(r"Item_\d+[A-Z]?", item_name)
                item_code = match.group(0) if match else ""

                if relevant_items is not None and not any(
                        re.match(f"^{pattern}([A-Z])?$", item_code) for pattern in relevant_items
                ):
                    print(f"File {index_file} does not match the query pattern(s) {relevant_items}. Skipping.")
                    continue

                index_path = os.path.join(doc_index_path, index_file)
                metadata_file = os.path.join(doc_metadata_path, f"{item_name}.npy")
                if not os.path.exists(metadata_file):
                    print(f"Metadata for {doc_folder} item {item_name} missing, skipping...")
                    continue

                print(f"Querying {doc_folder} - {item_name} with query: {query}")
                index, meta = load_index(index_path, metadata_file)
                # Retrieve initial answers from the FAISS index.
                results = retrieve_answers_from_pdf(query, index, meta, model, top_k=top_k)

                # Now augment each answer with adjacent passages.
                for answer in results:
                    file_field = answer.get("file", "")
                    passage_num = extract_passage_number(file_field)
                    # Set default texts for adjacent passages.
                    prev2_text, prev1_text, next1_text, next2_text = "", "", "", ""
                    if passage_num is not None:
                        # Compute adjacent passage numbers.
                        prev2_num = passage_num - 2
                        prev1_num = passage_num - 1
                        next1_num = passage_num + 1
                        next2_num = passage_num + 2

                        # Build the directory path where the passages are stored.
                        passage_dir = os.path.join(passages_root_dir, answer.get("document", ""), item_name)
                        # Build file paths for adjacent passages.
                        prev2_filepath = os.path.join(passage_dir, f"passage_{prev2_num}.txt")
                        prev1_filepath = os.path.join(passage_dir, f"passage_{prev1_num}.txt")
                        next1_filepath = os.path.join(passage_dir, f"passage_{next1_num}.txt")
                        next2_filepath = os.path.join(passage_dir, f"passage_{next2_num}.txt")
                        # Read the passage texts.
                        prev2_text = read_passage_text(prev2_filepath)
                        prev1_text = read_passage_text(prev1_filepath)
                        next1_text = read_passage_text(next1_filepath)
                        next2_text = read_passage_text(next2_filepath)
                    else:
                        print(f"Warning: Could not extract passage number from file field '{file_field}'")

                    # Get the core answer text.
                    answer_text = answer.get("text", "")
                    # Combine the adjacent passages and the core answer.
                    full_answer = f"{prev2_text}\n\n{prev1_text}\n\n{answer_text}\n\n{next1_text}\n\n{next2_text}".strip()
                    answer["full_answer"] = full_answer


                pdf_results.append({
                    "pdf_name": doc_folder,
                    "item": item_name,
                    "query": query,
                    "results": results
                })


        # ───────────────────────────────────────────────
        # Merge results per document into one JSON each
        # ───────────────────────────────────────────────
        merged_by_doc = {}

        for result in pdf_results:
            doc_name = result["pdf_name"]
            item = result["item"]
            answers = result["results"]

            if doc_name not in merged_by_doc:
                merged_by_doc[doc_name] = {
                    "document": doc_name,
                    "field": query,
                    "items": [],
                    "texts": []
                }

            merged_by_doc[doc_name]["items"].append(item)
            for ans in answers:
                full_text = ans.get("full_answer", "").strip()
                if full_text:
                    merged_by_doc[doc_name]["texts"].append(full_text)

        for doc_name, merged in merged_by_doc.items():
            combined_text = "\n\n".join(merged["texts"]).strip()

            # Create per-PDF directory under query_results_v2/
            doc_output_dir = os.path.join(output_query_dir, doc_name)
            os.makedirs(doc_output_dir, exist_ok=True)

            # Write the current field's JSON into the PDF's directory
            safe_field_name = re.sub(r'[^a-zA-Z0-9_\-]+', '_', query.strip()).lower()
            output_path = os.path.join(doc_output_dir, f"{safe_field_name}.json")

            with open(output_path, "w", encoding="utf-8") as f:
                json.dump({
                    "document": doc_name,
                    "field": merged["field"],
                    "items": merged["items"],
                    "combined_text": combined_text
                }, f, indent=4, ensure_ascii=False)
            print(f"[Merged] Saved field '{safe_field_name}' result to {output_path}")

    return pdf_results


def analyze_user_query(query):
    query = query.lower()

    if "sector" in query:
        return "sector"
    if "total revenue" in query or "net sales" in query:
        return "total_net_sales"
    if "net income" in query:
        return "net_income"
    if "earnings per share" in query or "eps" in query:
        return "eps"
    if "operating income" in query:
        return "operating_income"
    if "gross profit" in query:
        return "gross_profit"
    if "cash flow from operating activities" in query:
        return "cash_flow_operating_activities"
    if "capital expenditures" in query or "capex" in query:
        return "capital_expenditures"
    if "total assets" in query:
        return "total_assets"
    if "total liabilities" in query:
        return "total_liabilities"
    if "sales and marketing expense" in query:
        return "sales_and_marketing_expense"
    if "sg&a expense" in query or "general and administrative" in query:
        return "sga_expense"
    if "stock issuance" in query:
        return "stock_issuance"
    if "stock repurchases" in query or "stock buybacks" in query:
        return "stock_repurchases"
    if "fiscal year end" in query:
        return "fiscal_year_end"
    if "operating expenses" in query:
        return "operating_expenses"
    if "dividends paid" in query:
        return "dividends_paid"
    if "accounts receivable" in query:
        return "accounts_receivable"
    if "shareholder equity" in query or "shareholders' equity" in query:
        return "shareholder_equity"
    if "research and development expense" in query or "r&d expense" in query:
        return "research_and_development_expense"
    if "research and development investment" in query or "r&d investment" in query:
        return "research_and_development_investment"
    if "foreign revenue" in query:
        return "foreign_revenue"
    if "revenue streams" in query:
        return "revenue_streams"
    if "customer base" in query:
        return "customer_base"
    if "competitive landscape" in query:
        return "competitive_landscape"
    if "growth strategy" in query:
        return "growth_strategy"
    if "highlighted risks" in query or "key risks" in query:
        return "highlighted_risks"
    if "regulatory challenges" in query:
        return "regulatory_challenges"
    if "ebitda margin" in query:
        return "ebitda_margin"
    if "operating expense commentary" in query:
        return "operating_expense_commentary"
    if "valuation commentary" in query:
        return "valuation_commentary"
    if "capital expenditures projects" in query:
        return "capital_expenditures_projects"
    if "dividend and buyback policy" in query:
        return "dividend_and_buyback_policy"
    if "working capital efficiency" in query:
        return "working_capital_efficiency"
    if "management changes" in query:
        return "management_changes"
    if "supply chain disruptions" in query:
        return "supply_chain_disruptions"
    if "esg initiatives" in query:
        return "esg_initiatives"
    if "esg controversies" in query:
        return "esg_controversies"
    if "governance structure" in query:
        return "governance_structure"
    if "debt sustainability commentary" in query:
        return "debt_sustainability_commentary"
    if "debt refinancing activity" in query:
        return "debt_refinancing_activity"
    if "technology impact on operations" in query:
        return "technology_impact_on_operations"
    if "emerging tech investments" in query or "emerging technologies investments" in query:
        return "emerging_tech_investments"
    if "intellectual property assets" in query:
        return "intellectual_property_assets"
    if "research and development commentary" in query or "r&d commentary" in query:
        return "research_and_development_commentary"
    if "brand positioning" in query:
        return "brand_positioning"
    if "rebranding or marketing shift" in query:
        return "rebranding_or_marketing_shift"
    if "macroeconomic sensitivity" in query:
        return "macroeconomic_sensitivity"
    if "geopolitical and economic impacts" in query:
        return "geopolitical_and_economic_impacts"
    if "forward-looking statement" in query:
        return "forward_looking_statement"
    if "r&d expense" in query or "research and development expense" in query:
        return "Research_and_development_expense"
    if "r&d investment" in query or "research and development investment" in query:
        return "Research_and_development_investment"

    return None


def query_pdfs(query, index_dir, metadata_dir, output_dir, passages_root_dir):
    """
    Main function that:
      1) Loads the SentenceTransformer model,
      2) Builds a subfolder named after the query (e.g., 'total_revenue'),
      3) Calls 'query_all_pdfs' to retrieve and augment passages,
      4) Saves the results inside that query subfolder.
    """
    # Load SentenceTransformer model.
    model = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")

    query_output_dir = output_dir

    # Map queries to the relevant item names.
    processed_query = analyze_user_query(query)

    relevant_items = QUERY_ITEM_MAPPING.get(processed_query, None)

    # Query all PDF indices and save augmented results to the query subfolder.
    query_all_pdfs(
        query=query,
        index_base_dir=index_dir,
        metadata_base_dir=metadata_dir,
        model=model,
        output_query_dir=query_output_dir,
        passages_root_dir=passages_root_dir,
        top_k=3,
        relevant_items=relevant_items
    )


# ----------------------------
# Main Execution Block
# ----------------------------
if __name__ == "__main__":
    # Get the directory of this file (e.g., Engine/src)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Assume project root is one level up (Engine)
    project_root = os.path.dirname(current_dir)

    # Build absolute paths relative to the project root.
    index_dir = os.path.join(project_root, "embeddings", "index_per_pdf_items_v2")
    metadata_dir = os.path.join(project_root, "embeddings", "metadata_per_pdf_items_v2")
    output_dir = os.path.join(project_root, "output", "query_results_v2")
    # Root directory where the original split passages are stored.
    passages_root_dir = os.path.join(project_root, "data", "split_10k_items")

    # Convert directories to short paths to avoid Unicode issues.
    index_dir = get_short_path(index_dir)
    metadata_dir = get_short_path(metadata_dir)
    output_dir = get_short_path(output_dir)
    passages_root_dir = get_short_path(passages_root_dir)


    queries = [
        "Sector",
        "Total revenue",
        "Net income",
        "Earnings per share",
        "Operating income",
        "Gross profit",
        "Cash flow from operating activities",
        "Capital expenditures",
        "Total assets",
        "Total liabilities",
        "Sales and marketing expense",
        "SG&A expense",
        "Stock issuance",
        "Stock repurchases",
        "Fiscal year end",
        "Operating expenses",
        "Dividends paid",
        "Accounts receivable",
        "Shareholder equity",
        "Research and development expense",
        "Research and development investment",
        "Foreign revenue",
        "Revenue streams",
        "Customer base",
        "Competitive landscape",
        "Growth strategy",
        "Highlighted risks",
        "Regulatory challenges",
        "EBITDA margin",
        "Operating expense commentary",
        "Valuation commentary",
        "Capital expenditures projects",
        "Dividend and buyback policy",
        "Working capital efficiency",
        "Management changes",
        "Supply chain disruptions",
        "ESG initiatives",
        "ESG controversies",
        "Governance structure",
        "Debt sustainability commentary",
        "Debt refinancing activity",
        "Technology impact on operations",
        "Emerging tech investments",
        "Intellectual property assets",
        "Research and development commentary",
        "Brand positioning",
        "Rebranding or marketing shift",
        "Macroeconomic sensitivity",
        "Geopolitical and economic impacts",
        "Forward-looking statement"
    ]

    for base_query in queries:
        print(f"\nProcessing query: {base_query}")
        query_pdfs(
            query=base_query,
            index_dir=index_dir,
            metadata_dir=metadata_dir,
            output_dir=output_dir,
            passages_root_dir=passages_root_dir
        )