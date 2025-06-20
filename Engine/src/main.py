import os
os.environ["HF_HOME"] = "/cs/ep/110/HUJI-project/hf_cache"
os.environ["TRITON_CACHE_DIR"] = "/cs/ep/110/HUJI-project/hf_cache/triton_cache"
os.environ["TRANSFORMERS_CACHE"] = "/cs/ep/110/HUJI-project/hf_cache"
os.environ["HF_DATASETS_CACHE"] = "/cs/ep/110/HUJI-project/hf_cache"
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"


from Engine.src.llm_user_query import load_company_index
from pdf_to_text import split_pdf_to_items
from passage_preprocess import split_items_to_passages
from build_index import create_indexes
from query_engine import query_pdfs
from extract_fields import extract_metadata_table
from constants import PDF_DIR, ITEMS_DIR, SPLIT_PASSAGES, INDEX_BASE_PATH, METADATA_BASE_PATH
from try_queries import run_all_insights


def main():
    print("Step 1: Extracting items from PDFs...")
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    input_folder = os.path.join(base_path, "data", PDF_DIR)
    item_output_folder = os.path.join(base_path, "data", ITEMS_DIR)
    split_output_folder = os.path.join(base_path, "data", SPLIT_PASSAGES)
    index_output_folder = os.path.join(base_path, INDEX_BASE_PATH)
    metadata_output_folder = os.path.join(base_path, METADATA_BASE_PATH)

    # Step 1: Extract Items from PDFs
    split_pdf_to_items(input_folder, item_output_folder)

    # Step 2: Split each item file into passages
    print("Step 2: Splitting items into passages...")
    split_items_to_passages(item_output_folder, split_output_folder, passage_size=80)

    # Step 3: Create FAISS indexes
    print("Step 3: Encoding passages and building FAISS indices...")
    create_indexes(split_output_folder, index_output_folder, metadata_output_folder)

    # Step 4: Query the FAISS indices
    print("Step 4: Querying FAISS indices with predefined financial queries...")

    output_query_folder = os.path.join(base_path, "output", "query_results_v2")

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

    for query in queries:
        print(f"\n Running query: {query}")
        query_pdfs(
            query=query,
            index_dir=index_output_folder,
            metadata_dir=metadata_output_folder,
            output_dir=output_query_folder,
            passages_root_dir=split_output_folder
        )

    # Step 5: Extract final structured metadata
    print("Step 5: Extracting structured fields from LLM-augmented query results...")

    query_results_dir = output_query_folder
    company_tickers_path = os.path.join(base_path, "output", "company_tickers.json")
    company_tickers = load_company_index(company_tickers_path)
    final_df = extract_metadata_table(query_results_dir,company_tickers)

    output_csv_path = os.path.join(base_path, "output", "final_metadata_table_numeric_v1_prompt.csv")
    final_df.to_csv(output_csv_path, index=False)

    print(f"[Saved] Final metadata table written to {output_csv_path}")

    # # Step 6: Run Insight Queries (for example/demo)
    # print("\nStep 6: Running Insight Queries from final_metadata_table.csv...\n")
    # run_all_insights()


if __name__ == '__main__':
    main()
