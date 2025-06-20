import requests
import pandas as pd
import multiprocessing
# from pandarallel import pandarallel
from sec_api import QueryApi,ExtractorApi
import os
from sec_api import PdfGeneratorApi
from sec_api import XbrlApi
from consts import *
from concurrent.futures import ProcessPoolExecutor
import re

# # Initialize pandarallel
# pandarallel.initialize(nb_workers=4, progress_bar=True, use_memory_fs=False)

# Functions
def initialize_extractor(api_key):
    """Initialize the SEC Extractor API."""
    return ExtractorApi(api_key)


def extract_section_html(extractor, filing_url, section="8"):
    """Extract a specific section as HTML."""
    return extractor.get_section(filing_url, section, "html")

def download_csv_file(url, output_file):
    """Download CSV file from a URL."""
    response = requests.get(url)
    with open(output_file, "wb") as f:
        f.write(response.content)
    print(f"CSV file saved as {output_file}")

def clean_csv(file_path, start=0, end=None):
    """
    Load and clean the Russell 3000 constituents CSV file.

    Parameters:
        file_path (str): Path to the Russell 3000 CSV file.
        start (int): The starting index (inclusive) for the range of rows.
        end (int): The ending index (exclusive) for the range of rows.

    Returns:
        pd.DataFrame: A cleaned DataFrame containing rows in the specified range.
    """
    # Load the CSV and skip the first 9 metadata rows, remove last 2 rows
    df = pd.read_csv(file_path, skiprows=9).iloc[:-2]

    # Slice the DataFrame to return rows within the specified range
    df = df.iloc[start:end]

    print(f"Number of constituents in range {start} to {end}: {len(df)}")
    return df


def create_batches(tickers, batch_size=100):
    """Split tickers into batches."""
    return [list(tickers[i:i + batch_size]) for i in range(0, len(tickers), batch_size)]

def get_10K_filing_urls(row, query_api):
    """Fetch 10-K filing URLs for a batch of tickers."""
    ticker_batch = row["Tickers"]
    if not ticker_batch:
        return []

    ticker_query = " OR ".join([f'ticker:"{ticker}"' for ticker in ticker_batch])
    date_query = "filedAt:[2014-01-01 TO 2025-12-31]"
    form_type_query = 'formType:"10-K" AND NOT formType:"10-K/A" AND NOT formType:"NT"'
    search_query = f"({ticker_query}) AND {date_query} AND {form_type_query}"

    search_params = {
        "query": search_query,
        "from": 0,
        "size": 50,
        "sort": [{"filedAt": {"order": "desc"}}],
    }

    filing_urls = []
    while True:
        search_results = query_api.get_filings(search_params)
        filings = search_results["filings"]
        if not filings:
            break

        metadata = [
            {
                "companyName": f['companyName'],
                "ticker": f["ticker"],
                "cik": f["cik"],
                "filedAt": f["filedAt"],
                "accessionNo": f["accessionNo"],
                "filingUrl": f["linkToFilingDetails"],
            }
            for f in filings
        ]
        filing_urls.extend(metadata)
        search_params["from"] += search_params["size"]

    return pd.DataFrame(filing_urls)

def save_metadata_to_csv(metadata_df, output_file):
    """Save metadata DataFrame to a CSV file."""
    metadata_df.to_csv(output_file, index=False)
    print(f"Metadata saved to {output_file}")

def save_html_files(metadata_df,section="8", output_folder="html_files"):
    extractor_api = ExtractorApi(api_key=SEC_API_KEY)
    """Download and save HTML content for each filing URL."""
    # Create the output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Iterate over each filing URL
    for idx, row in metadata_df.iterrows():
        filing_url = row["filingUrl"]
        ticker = row["ticker"]
        accession_no = row["accessionNo"]
        company_name = row['companyName']
        file_name = f"{company_name}_{ticker}_{accession_no}.pdf"
        file_path = os.path.join(output_folder, file_name)

        try:
            # Fetch the HTML content using ExtractorApi
            html_content = extractor_api.get_section(filing_url, section, "html")
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(html_content)
            print(f"Saved: {file_path}")
        except Exception as e:
            print(f"Failed to save {file_name}: {e}")

def load_metadata(file_path):
    """Load metadata from a CSV file."""
    return pd.read_csv(file_path)


def save_pdf_files(metadata_df,output_folder="html_files"):
    """Download and save PDF content for each filing URL."""
    pdfGeneratorApi = PdfGeneratorApi(api_key=SEC_API_KEY)
    # Create the output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Iterate over each filing URL
    for idx, row in metadata_df.iterrows():
        filing_url = row["filingUrl"]
        ticker = row["ticker"]
        accession_no = row["accessionNo"]
        company_name = row['companyName']
        file_name = f"{company_name}_{ticker}_{accession_no}.pdf"
        file_path = os.path.join(output_folder, file_name)

        try:
            pdf_content = pdfGeneratorApi.get_pdf(filing_url)
            # Fetch the PDF content using ExtractorApi
            with open(file_path, "wb") as file:
                file.write(pdf_content)
            print(f"Saved: {file_path}")
        except Exception as e:
            print(f"Failed to save {file_name}: {e}")


def fetch_and_update_metadata_with_json(metadata_df, output_file):
    """
    Fetch Net Income from XBRL JSON for each filing URL and update the metadata DataFrame.

    Parameters:
        metadata_df (pd.DataFrame): A pandas DataFrame containing metadata,
                                    including filing URLs and associated details.
        output_file (str): Path to save the updated metadata CSV file.
        sec_api_key (str): API key for the SEC XBRL API.
    # Load metadata CSV
    """

    # Initialize the XBRL API
    xbrlApi = XbrlApi(SEC_API_KEY)

    # Add a new column for Net Income (initialize with None)
    metadata_df["NetIncome"] = None

    for idx, row in metadata_df.iterrows():
        htm_url = row["filingUrl"]  # Get the URL for the current filing

        try:
            filed_at = row["filedAt"]
            year = filed_at.split("-")[0]  # Extract the year from "YYYY-MM-DD"

            # Fetch XBRL JSON data
            xbrl_json = xbrlApi.xbrl_to_json(htm_url=htm_url)
            date_report_is_about = xbrl_json["CoverPage"]['DocumentPeriodEndDate']
            net_income = ''
            for net_income_val in xbrl_json["StatementsOfIncome"]['NetIncomeLoss']:
                if net_income_val['period']['endDate'] == date_report_is_about:
                    # Extract Net Income
                    # net_income =  str(abs(int(net_income_val['value'])))
                    net_income =  net_income_val['value']
                    break

            # Update the Net Income in the DataFrame
            metadata_df.at[idx, "NetIncome"] = net_income

            print(f"Fetched Net Income for {row['ticker']} ({year}): {net_income}")
        except Exception as e:
            print(f"Failed to fetch Net Income for {row['ticker']} (URL: {htm_url}): {e}")

    # Save the updated DataFrame to a new CSV file
    metadata_df.to_csv(output_file, index=False)
    print(f"Updated metadata saved to {output_file}")


def process_row(row_query_api_tuple):
    """Wrapper function to call get_10K_filing_urls."""
    row, query_api = row_query_api_tuple
    return get_10K_filing_urls(row, query_api)


def parallel_get_10K_filing_urls(ticker_batches_df, query_api):
    """Apply get_10K_filing_urls function in parallel using concurrent.futures."""
    # Prepare arguments as tuples to pass to process_row
    args = [(row, query_api) for _, row in ticker_batches_df.iterrows()]

    with ProcessPoolExecutor(max_workers=4) as executor:
        results = list(executor.map(process_row, args))
    return results

# # Main workflow
def main():
    # # Step 1: Download and clean CSV
    # download_csv_file(CSV_URL, CSV_FILE)
    # russell_3000 = clean_csv(CSV_FILE,start=9,end=12)
    #
    # # Step 2: Create batches of tickers
    # ticker_batches = create_batches(russell_3000["Ticker"], batch_size=100)
    # ticker_batches_df = pd.DataFrame({"Tickers": ticker_batches})
    #
    # # Step 3: Query 10-K filings
    # query_api = QueryApi(api_key=SEC_API_KEY)
    #
    # metadata_results = parallel_get_10K_filing_urls(ticker_batches_df, query_api)
    # metadata = pd.concat(metadata_results, ignore_index=True)
    #
    # # Step 4: Save metadata to CSV or load from existing (uncomment relevant part)
    # save_metadata_to_csv(metadata, METADATA_FILE)
    #
    metadata = load_metadata("russell-3000-10k-filing-urls_2025-05-26_20-59-27.csv")

    # Step 5: Download and save HTML/PDF filings
    # save_html_files(metadata, output_folder=HTML_FOLDER)
    save_pdf_files(metadata,output_folder=PDF_FOLDER)

    # fetch_and_update_metadata_with_json(metadata,output_file="updated_metadata.csv")

if __name__ == "__main__":
    # multiprocessing.set_start_method("spawn", force=True)
    main()

