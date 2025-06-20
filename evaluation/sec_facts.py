import requests
import json
import pandas as pd

def load_companies_map(json_path):
    """
    Load local company_tickers.json and build a ticker → CIK mapping.
    """
    with open(json_path, 'r') as f:
        data = json.load(f)

    # Convert to DataFrame for flexibility
    records = []
    for entry in data.values():
        records.append({
            "ticker": entry["ticker"].upper(),
            "cik": str(entry["cik_str"]).zfill(10),
            "title": entry["title"]
        })

    df = pd.DataFrame(records)
    df.set_index('ticker', inplace=True)
    return df

def get_cik_from_ticker(ticker, df):
    """
    Retrieve CIK for a given ticker from the loaded DataFrame.
    """
    ticker = ticker.upper()
    if ticker in df.index:
        return df.loc[ticker, 'cik']
    return None

def get_cik_from_company_name(name, df):
    """
    Retrieve CIK from a company name (case-insensitive exact match).
    """
    name = name.upper().strip()
    match = df[df['title'].str.upper().str.strip() == name]

    if not match.empty:
        return match.iloc[0]['cik']
    else:
        return None

def get_cik_from_ticker_with_url(ticker):
    url = "https://www.sec.gov/files/company_tickers.json"
    headers = {"User-Agent": "Your Name your@email.com"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    data = response.json()

    for entry in data.values():
        if entry["ticker"].lower() == ticker.lower():
            return str(entry["cik_str"]).zfill(10)
    return None

def get_company_facts(cik):
    headers = {"User-Agent": "Your Name your@email.com"}
    url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

def extract_annual_facts(facts_json, us_gaap_field):
    results = {}
    try:
        data_points = facts_json["facts"]["us-gaap"][us_gaap_field]["units"]["USD"]
        for item in data_points:
            frame = item.get("frame")
            if frame and frame.startswith("CY") and len(frame) == len("CY2023"):
                year = frame[2:]  # Extract year, e.g., "2023"
                val = item.get("val")
                if val is not None:
                    results[year] = val
    except KeyError:
        pass
    return results


def get_facts_for_years(ticker, years, us_gaap_field, ticker_cik_df):
    """
    Given a ticker, list of years, and a fact name (XBRL US-GAAP tag),
    return the annual fact values for the specified years.
    """
    cik = get_cik_from_ticker(ticker, ticker_cik_df)
    if not cik:
        print(f"[!] Ticker {ticker} not found.")
        return {}

    facts = get_company_facts(cik)
    annual_data = extract_annual_facts(facts, us_gaap_field)

    # Filter only for the requested years
    filtered_data = {year: val for year, val in annual_data.items() if year in years}

    return filtered_data

# Example usage:
if __name__ == "__main__":
    tic_df = load_companies_map("company_tickers.json")
    ticker = 'AAPL'
    get_facts_for_years(ticker,['2022','2023','2024'],'NetIncomeLoss',tic_df)

