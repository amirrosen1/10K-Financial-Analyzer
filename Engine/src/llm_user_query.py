import os
os.environ["HF_HOME"] = "/cs/ep/110/HUJI-project/hf_cache"
os.environ["TRANSFORMERS_CACHE"] = "/cs/ep/110/HUJI-project/hf_cache"
os.environ["HF_DATASETS_CACHE"] = "/cs/ep/110/HUJI-project/hf_cache"
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

import sys
import json
import pdfplumber
import re
import unicodedata
from rapidfuzz import fuzz, process

import logging
logging.getLogger("pdfminer").setLevel(logging.ERROR)


current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from prompts import (
    EXTRACT_COMPANY_NAME_PROMPT,
    EXTRACT_FILING_YEAR_PROMPT,
    EXTRACT_COMPANY_YEAR_PROMPT,
    EXTRACT_SECTOR_PROMPT,
    EXTRACT_TOTAL_REVENUE_PROMPT,
    EXTRACT_NET_INCOME_PROMPT,
    EXTRACT_EPS_PROMPT,
    EXTRACT_OPERATING_INCOME_PROMPT,
    EXTRACT_GROSS_PROFIT_PROMPT,
    EXTRACT_CASH_FLOW_OPERATING_ACTIVITIES_PROMPT,
    EXTRACT_CAPITAL_EXPENDITURES_PROMPT,
    EXTRACT_TOTAL_ASSETS_PROMPT,
    EXTRACT_TOTAL_LIABILITIES_PROMPT,
    EXTRACT_SALES_AND_MARKETING_EXPENSE_PROMPT,
    EXTRACT_SG_A_EXPENSE_PROMPT,
    EXTRACT_STOCK_ISSUANCE_PROMPT,
    EXTRACT_STOCK_REPURCHASES_PROMPT,
    EXTRACT_FISCAL_YEAR_END_PROMPT,
    EXTRACT_OPERATING_EXPENSES_PROMPT,
    EXTRACT_DIVIDENDS_PAID_PROMPT,
    EXTRACT_ACCOUNTS_RECEIVABLE_PROMPT,
    EXTRACT_SHAREHOLDER_EQUITY_PROMPT,
    EXTRACT_RESEARCH_AND_DEVELOPMENT_EXPENSE_PROMPT,
    EXTRACT_RESEARCH_AND_DEVELOPMENT_INVESTMENT_PROMPT,
    EXTRACT_FOREIGN_REVENUE_PROMPT,
    EXTRACT_REVENUE_STREAMS_PROMPT,
    EXTRACT_CUSTOMER_BASE_PROMPT,
    EXTRACT_COMPETITIVE_LANDSCAPE_PROMPT,
    EXTRACT_GROWTH_STRATEGY_PROMPT,
    EXTRACT_HIGHLIGHTED_RISKS_PROMPT,
    EXTRACT_REGULATORY_CHALLENGES_PROMPT,
    EXTRACT_NET_INCOME_TREND_PROMPT,
    EXTRACT_EBITDA_MARGIN_PROMPT,
    EXTRACT_OPERATING_EXPENSE_COMMENTARY_PROMPT,
    EXTRACT_VALUATION_COMMENTARY_PROMPT,
    EXTRACT_CAPEX_PROJECTS_PROMPT,
    EXTRACT_DIVIDEND_AND_BUYBACK_POLICY_PROMPT,
    EXTRACT_WORKING_CAPITAL_EFFICIENCY_PROMPT,
    EXTRACT_SUPPLY_CHAIN_DISRUPTIONS_PROMPT,
    EXTRACT_MANAGEMENT_CHANGES_PROMPT,
    EXTRACT_ESG_INITIATIVES_PROMPT,
    EXTRACT_ESG_CONTROVERSIES_PROMPT,
    EXTRACT_GOVERNANCE_STRUCTURE_PROMPT,
    EXTRACT_DEBT_SUSTAINABILITY_COMMENTARY_PROMPT,
    EXTRACT_DEBT_REFINANCING_ACTIVITY_PROMPT,
    EXTRACT_TECHNOLOGY_IMPACT_ON_OPERATIONS_PROMPT,
    EXTRACT_EMERGING_TECH_INVESTMENTS_PROMPT,
    EXTRACT_IP_ASSETS_PROMPT,
    EXTRACT_R_AND_D_COMMENTARY_PROMPT,
    EXTRACT_BRAND_POSITIONING_PROMPT,
    EXTRACT_REBRANDING_OR_MARKETING_SHIFT_PROMPT,
    EXTRACT_MACROECONOMIC_SENSITIVITY_PROMPT,
    EXTRACT_GEOPOLITICAL_AND_ECONOMIC_IMPACTS_PROMPT,
    EXTRACT_GROWTH_SCENARIOS_PROMPT,
    EXTRACT_FORWARD_LOOKING_STATEMENT_PROMPT,
)

from Engine.src.mistral_7b import get_model_and_tokenizer, invoke_model

# -------------------------------
# Base Utilities
# -------------------------------
def load_combined_text(folder_name, field):
    try:
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        json_path = os.path.join(project_root, "output", "query_results_v2", folder_name, f"{field}.json")

        if not os.path.exists(json_path):
            print(f"[Warning] {field}.json not found for: {folder_name}")
            return ""

        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("combined_text", "")
    except Exception as e:
        print(f"[Error] Failed to load {field}.json for {folder_name}: {e}")
        return ""


def run_llm_prompt(prompt):
    model, tokenizer = get_model_and_tokenizer()
    return invoke_model(prompt).strip()


# -------------------------------
# Company and Sector
# -------------------------------
def extract_company_and_year(folder_name):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    pdfs_folder = os.path.join(project_root, "data", "pdfs")

    pdf_filename = next((f for f in os.listdir(pdfs_folder) if f.startswith(folder_name) and f.endswith(".pdf")), None)
    if not pdf_filename:
        print(f"PDF for folder '{folder_name}' not found in {pdfs_folder}")
        return "", ""

    pdf_path = os.path.join(pdfs_folder, pdf_filename)

    try:
        with pdfplumber.open(pdf_path) as pdf:
            first_page_text = pdf.pages[0].extract_text()

        if not first_page_text or len(first_page_text.strip()) < 30:
            raise ValueError("First page appears empty or malformed")

        prompt = EXTRACT_COMPANY_YEAR_PROMPT.replace("<page>", first_page_text)
        response = run_llm_prompt(prompt)
        result = json.loads(response)
        return result.get("company_name", ""), result.get("year", "")
    except Exception as e:
        print(f"Error extracting company/year from {folder_name}: {e}")
        return "", ""


def get_first_page_text(folder_name):
    import pdfplumber
    import os

    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    pdfs_folder = os.path.join(project_root, "data", "pdfs")
    pdf_filename = next((f for f in os.listdir(pdfs_folder) if f.startswith(folder_name) and f.endswith(".pdf")), None)

    if not pdf_filename:
        print(f"[Error] PDF for folder '{folder_name}' not found in {pdfs_folder}")
        return ""

    pdf_path = os.path.join(pdfs_folder, pdf_filename)

    try:
        with pdfplumber.open(pdf_path) as pdf:
            page = pdf.pages[0]
            full_text = page.extract_text()
            if not full_text or len(full_text.strip()) < 30:
                print(f"[Error] First page is empty or malformed for {folder_name}")
                return ""

            words = page.extract_words()
            half_page_height = page.height / 2

            # Build a set of words from top half of the page
            top_words_set = set(word['text'] for word in words if word['top'] < half_page_height)

            # Filter lines that contain at least one top-half word
            top_half_lines = [
                line for line in full_text.split("\n")
                if any(token in top_words_set for token in line.split())
            ]

            first_page_text = "\n".join(top_half_lines)
            if not first_page_text or len(first_page_text.strip()) < 30:
                print(f"[Error] Top half of first page is empty or malformed for {folder_name}")
                return ""

            return first_page_text

    except Exception as e:
        print(f"[Error] Failed to read PDF for {folder_name}: {e}")
        return ""


def normalize_line(line):
    line = unicodedata.normalize("NFKC", line).strip()
    # Remove leading f" or " or ' if present
    return line.lstrip("f'\"").rstrip("'\"")

def extract_company_name(folder_name):
    first_page_text = get_first_page_text(folder_name)
    if not first_page_text:
        return ""

    prompt = EXTRACT_COMPANY_NAME_PROMPT.replace("<page>", first_page_text)
    print(f"[DEBUG] Prompt for company name:\n{prompt}\n")

    response = run_llm_prompt(prompt)
    print(f"[DEBUG] Raw LLM response:\n{response}\n")

    lines = response.strip().splitlines()
    name = ""

    # Step 1: Try known LLM formats
    patterns = [
        r"Company Name:\s*(.+)",
        r"Company Name\s*-\s*(.+)",
        r"Company Name\s+(.+)"
    ]

    for line in lines:
        norm_line = normalize_line(line)
        for pattern in patterns:
            match = re.match(pattern, norm_line, re.IGNORECASE)
            if match:
                name = match.group(1).strip().rstrip(".")
                print(f"[DEBUG] Matched using pattern '{pattern}': {name}")
                break
        if name:
            break

    # Step 2: Fallback heuristic
    if not name:
        for line in lines:
            norm_line = normalize_line(line)
            if norm_line.lower().startswith("company name:"):
                candidate = norm_line.split(":", 1)[1].strip()
            else:
                candidate = norm_line

            if re.match(r"^[A-Z][A-Za-z0-9\s\.\-&,'()]+$", candidate) and len(candidate.split()) >= 2:
                name = candidate.rstrip(".")
                print(f"[DEBUG] Heuristic fallback match: {name}")
                break
        else:
            # Final fallback: last line after colon split
            if lines:
                fallback = normalize_line(lines[-1])
                name = fallback.split(":", 1)[-1].strip().rstrip(".")
                print(f"[DEBUG] Fallback to last line: {name}")
            else:
                name = ""

    print(f"[DEBUG] Final company name extracted: {name}")
    return name

def normalize_name(name):
    name = unicodedata.normalize("NFKC", name).lower()
    replacements = {
        "corporation": "corp",
        "incorporated": "inc",
        "co.": "company",
        "co": "company",
        "&": "and",
        ".": "",
        ",": "",
    }
    for old, new in replacements.items():
        name = name.replace(old, new)
    return name.strip()

def load_company_index(json_path):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    return [
        {
            "original": c.get("title", ""),
            "normalized": normalize_name(c.get("title", "")),
            "cik": str(c["cik_str"]).zfill(10)  # Zero-pad CIKs if needed
        }
        for c in data.values()
    ]


def match_company_name_to_cik(extracted_name, company_db, threshold=80):
    # Step 1: Convert dict-of-dicts to list-of-dicts if necessary
    if isinstance(company_db, dict):
        print("[DEBUG] Converting company_db from dict to list of dicts")
        company_db = [
            {
                "original": entry.get("title", ""),
                "normalized": normalize_name(entry.get("title", "")),
                "cik": str(entry["cik_str"]).zfill(10)
            }
            for entry in company_db.values()
        ]

    # Step 2: Normalize the extracted name and candidates
    normalized_extracted = normalize_name(extracted_name)
    print(f"[DEBUG] Normalized extracted name: {normalized_extracted}")

    candidates = [c["normalized"] for c in company_db]
    print(f"[DEBUG] Number of candidate names: {len(candidates)}")

    # Step 3: Fuzzy match using RapidFuzz
    try:
        best_match, score, _ = process.extractOne(
            normalized_extracted, candidates, scorer=fuzz.ratio
        )
        print(f"[DEBUG] Best match: {best_match} (Score: {score})")
    except Exception as e:
        print(f"[ERROR] Fuzzy matching failed: {e}")
        return None, None

    # Step 4: Locate full record
    matched = next((c for c in company_db if c["normalized"] == best_match), None)

    if matched and score >= threshold:
        print(f"[DEBUG] Fuzzy match successful: '{extracted_name}' → '{matched['original']}' (Score: {score})")
        print(f"[DEBUG] Returning: ({matched['original']}, {matched['cik']})")
        return matched["original"], matched["cik"]
    else:
        print(f"[WARNING] No confident fuzzy match found for '{extracted_name}' (Score: {score})")
        return None, None


def extract_filing_year(folder_name):
    import re
    first_page_text = get_first_page_text(folder_name)
    if not first_page_text:
        return None

    prompt = EXTRACT_FILING_YEAR_PROMPT.replace("<page>", first_page_text)
    response = run_llm_prompt(prompt).strip()

    # Extract a 4-digit year anywhere in the response
    match = re.search(r"\b(20\d{2})\b", response)
    if match:
        return int(match.group(1))

    print(f"[Error] Could not parse year from response: {response}")
    return None


def extract_sector(folder_name):
    combined_text = load_combined_text(folder_name, "sector")
    if not combined_text:
        return ""
    prompt = EXTRACT_SECTOR_PROMPT.replace("<document>", combined_text)
    return run_llm_prompt(prompt)


# -------------------------------
# Financial Field Extractors
# -------------------------------
def extract_total_revenue(folder_name, year):
    if not year:
        return ""
    combined_text = load_combined_text(folder_name, "total_revenue")
    if not combined_text:
        return ""
    prompt = EXTRACT_TOTAL_REVENUE_PROMPT.replace("<document>", combined_text).replace("<year>", str(year))
    return run_llm_prompt(prompt)

def extract_net_income(folder_name, year):
    if not year:
        return ""
    combined_text = load_combined_text(folder_name, "net_income")
    if not combined_text:
        return ""
    prompt = EXTRACT_NET_INCOME_PROMPT.replace("<document>", combined_text).replace("<year>", str(year))
    return run_llm_prompt(prompt)

def extract_eps(folder_name, year):
    if not year:
        return ""
    combined_text = load_combined_text(folder_name, "earnings_per_share")
    if not combined_text:
        return ""
    prompt = EXTRACT_EPS_PROMPT.replace("<document>", combined_text).replace("<year>", str(year))
    return run_llm_prompt(prompt)

def extract_operating_income(folder_name, year):
    if not year:
        return ""
    combined_text = load_combined_text(folder_name, "operating_income")
    if not combined_text:
        return ""
    prompt = EXTRACT_OPERATING_INCOME_PROMPT.replace("<document>", combined_text).replace("<year>", str(year))
    return run_llm_prompt(prompt)

def extract_gross_profit(folder_name, year):
    if not year:
        return ""
    combined_text = load_combined_text(folder_name, "gross_profit")
    if not combined_text:
        return ""
    prompt = EXTRACT_GROSS_PROFIT_PROMPT.replace("<document>", combined_text).replace("<year>", str(year))
    return run_llm_prompt(prompt)

def extract_cash_flow_operating_activities(folder_name, year):
    if not year:
        return ""
    combined_text = load_combined_text(folder_name, "cash_flow_from_operating_activities")
    if not combined_text:
        return ""
    prompt = EXTRACT_CASH_FLOW_OPERATING_ACTIVITIES_PROMPT.replace("<document>", combined_text).replace("<year>", str(year))
    return run_llm_prompt(prompt)

def extract_capital_expenditures(folder_name, year):
    if not year:
        return ""
    combined_text = load_combined_text(folder_name, "capital_expenditures")
    if not combined_text:
        return ""
    prompt = EXTRACT_CAPITAL_EXPENDITURES_PROMPT.replace("<document>", combined_text).replace("<year>", str(year))
    return run_llm_prompt(prompt)

def extract_total_assets(folder_name, year):
    if not year:
        return ""
    combined_text = load_combined_text(folder_name, "total_assets")
    if not combined_text:
        return ""
    prompt = EXTRACT_TOTAL_ASSETS_PROMPT.replace("<document>", combined_text).replace("<year>", str(year))
    return run_llm_prompt(prompt)

def extract_total_liabilities(folder_name, year):
    if not year:
        return ""
    combined_text = load_combined_text(folder_name, "total_liabilities")
    if not combined_text:
        return ""
    prompt = EXTRACT_TOTAL_LIABILITIES_PROMPT.replace("<document>", combined_text).replace("<year>", str(year))
    return run_llm_prompt(prompt)

def extract_sales_and_marketing_expense(folder_name, year):
    if not year:
        return ""
    combined_text = load_combined_text(folder_name, "sales_and_marketing_expense")
    if not combined_text:
        return ""
    prompt = EXTRACT_SALES_AND_MARKETING_EXPENSE_PROMPT.replace("<document>", combined_text).replace("<year>", str(year))
    return run_llm_prompt(prompt)

def extract_sg_a_expense(folder_name, year):
    if not year:
        return ""
    combined_text = load_combined_text(folder_name, "sg_a_expense")
    if not combined_text:
        return ""
    prompt = EXTRACT_SG_A_EXPENSE_PROMPT.replace("<document>", combined_text).replace("<year>", str(year))
    return run_llm_prompt(prompt)

def extract_general_and_administrative_expense(folder_name, year):
    if not year:
        return ""
    combined_text = load_combined_text(folder_name, "sg_a_expense")
    if not combined_text:
        return ""
    prompt = """
    You are an expert in extracting financial values from 10-Ks.

    xtract the **General and Administrative (G&A)** expense from the document for the year <year>.

    Document:
    <document>

    Instructions:
    - Return only the G&A expense.
    - Do NOT return Operating Income or Total Operating Expenses.
    - If G&A is not available, return "N/A".
    """.replace("<document>", combined_text).replace("<year>", str(year))
    return run_llm_prompt(prompt)

def extract_stock_issuance(folder_name, year):
    if not year:
        return ""
    combined_text = load_combined_text(folder_name, "stock_issuance")
    if not combined_text:
        return ""
    prompt = EXTRACT_STOCK_ISSUANCE_PROMPT.replace("<document>", combined_text).replace("<year>", str(year))
    return run_llm_prompt(prompt)

def extract_stock_repurchases(folder_name, year):
    if not year:
        return ""
    combined_text = load_combined_text(folder_name, "stock_repurchases")
    if not combined_text:
        return ""
    prompt = EXTRACT_STOCK_REPURCHASES_PROMPT.replace("<document>", combined_text).replace("<year>", str(year))
    return run_llm_prompt(prompt)

def extract_fiscal_year_end(folder_name, year):
    if not year:
        return ""
    combined_text = load_combined_text(folder_name, "fiscal_year_end")
    if not combined_text:
        return ""
    prompt = EXTRACT_FISCAL_YEAR_END_PROMPT.replace("<document>", combined_text).replace("<year>", str(year))
    return run_llm_prompt(prompt)

def extract_operating_expenses(folder_name, year):
    if not year:
        return ""
    combined_text = load_combined_text(folder_name, "operating_expenses")
    if not combined_text:
        return ""
    prompt = EXTRACT_OPERATING_EXPENSES_PROMPT.replace("<document>", combined_text).replace("<year>", str(year))
    return run_llm_prompt(prompt)

def extract_dividends_paid(folder_name, year):
    if not year:
        return ""
    combined_text = load_combined_text(folder_name, "dividends_paid")
    if not combined_text:
        return ""
    prompt = EXTRACT_DIVIDENDS_PAID_PROMPT.replace("<document>", combined_text).replace("<year>", str(year))
    return run_llm_prompt(prompt)

def extract_accounts_receivable(folder_name, year):
    if not year:
        return ""
    combined_text = load_combined_text(folder_name, "accounts_receivable")
    if not combined_text:
        return ""
    prompt = EXTRACT_ACCOUNTS_RECEIVABLE_PROMPT.replace("<document>", combined_text).replace("<year>", str(year))
    return run_llm_prompt(prompt)

def extract_shareholder_equity(folder_name, year):
    if not year:
        return ""
    combined_text = load_combined_text(folder_name, "shareholder_equity")
    if not combined_text:
        return ""
    prompt = EXTRACT_SHAREHOLDER_EQUITY_PROMPT.replace("<document>", combined_text).replace("<year>", str(year))
    return run_llm_prompt(prompt)

def extract_research_and_development_expense(folder_name, year):
    if not year:
        return ""
    combined_text = load_combined_text(folder_name, "research_and_development_expense")
    if not combined_text:
        return ""
    prompt = EXTRACT_RESEARCH_AND_DEVELOPMENT_EXPENSE_PROMPT.replace("<document>", combined_text).replace("<year>", str(year))
    return run_llm_prompt(prompt)

def extract_research_and_development_investment(folder_name, year):
    if not year:
        return ""
    combined_text = load_combined_text(folder_name, "research_and_development_investment")
    if not combined_text:
        return ""
    prompt = EXTRACT_RESEARCH_AND_DEVELOPMENT_INVESTMENT_PROMPT.replace("<document>", combined_text).replace("<year>", str(year))
    return run_llm_prompt(prompt)

def extract_foreign_revenue(folder_name, year):
    if not year:
        return ""
    combined_text = load_combined_text(folder_name, "foreign_revenue")
    if not combined_text:
        return ""
    prompt = EXTRACT_FOREIGN_REVENUE_PROMPT.replace("<document>", combined_text).replace("<year>", str(year))
    return run_llm_prompt(prompt)

# ----------------------------------
# Financial Verbal Field Extractors
# ----------------------------------

def extract_revenue_streams_summary(folder_name, year, company_name):
    """
    Extracts a qualitative summary about revenue streams and how they've evolved over the past three years.
    Only uses current year's revenue_streams text, and mentions past two years in the question.
    """
    combined_text = load_combined_text(folder_name, "revenue_streams")
    if not combined_text:
        return ""

    if not year:
        print(f"[Error] Year is None for {folder_name}")
        return ""

    year = int(year)
    prompt = EXTRACT_REVENUE_STREAMS_PROMPT \
        .replace("<year>", str(year)) \
        .replace("<year_minus_1>", str(year - 1)) \
        .replace("<year_minus_2>", str(year - 2)) \
        .replace("<document>", combined_text) \
        .replace("<company_name>", company_name)

    return run_llm_prompt(prompt)

def extract_customer_base(folder_name, year, company_name):
    combined_text = load_combined_text(folder_name, "customer_base")
    if not combined_text:
        return ""
    prompt = EXTRACT_CUSTOMER_BASE_PROMPT.replace("<document>", combined_text).replace("<year>", str(year)).replace("<company_name>", company_name)
    return run_llm_prompt(prompt)

def extract_competitive_landscape(folder_name, year, company_name):
    combined_text = load_combined_text(folder_name, "competitive_landscape")
    if not combined_text:
        return ""
    prompt = EXTRACT_COMPETITIVE_LANDSCAPE_PROMPT.replace("<document>", combined_text).replace("<year>", str(year)).replace("<company_name>", company_name)
    return run_llm_prompt(prompt)

def extract_growth_strategy(folder_name, year, company_name):
    combined_text = load_combined_text(folder_name, "growth_strategy")
    if not combined_text:
        return ""
    prompt = EXTRACT_GROWTH_STRATEGY_PROMPT.replace("<document>", combined_text).replace("<year>", str(year)).replace("<company_name>", company_name)
    return run_llm_prompt(prompt)

def extract_highlighted_risks(folder_name, year, company_name):
    combined_text = load_combined_text(folder_name, "highlighted_risks")
    if not combined_text:
        return ""
    prompt = EXTRACT_HIGHLIGHTED_RISKS_PROMPT.replace("<document>", combined_text).replace("<year>", str(year)).replace("<company_name>", company_name)
    return run_llm_prompt(prompt)

def extract_regulatory_challenges(folder_name, year, company_name):
    combined_text = load_combined_text(folder_name, "regulatory_challenges")
    if not combined_text:
        return ""
    prompt = EXTRACT_REGULATORY_CHALLENGES_PROMPT.replace("<document>", combined_text).replace("<year>", str(year)).replace("<company_name>", company_name)
    return run_llm_prompt(prompt)

def extract_net_income_trend_summary(folder_name, year, company_name, current_net_income):
    if not year:
        print(f"[Error] Year is None for {folder_name}")
        return ""
    if not company_name:
        print(f"[Error] Company name is None for {folder_name}")
        return ""

    combined_text = load_combined_text(folder_name, "net_income")
    if not combined_text:
        return ""

    try:
        year = int(year)
    except ValueError:
        print(f"[Error] Year conversion failed for {folder_name}: {year}")
        return ""

    prev_year = year - 1
    prev_year_2 = year - 2

    # Since we removed df, we'll use "N/A" for past values
    net_income_y1 = "N/A"
    net_income_y2 = "N/A"
    net_income_y3 = str(current_net_income or "N/A")

    prompt = EXTRACT_NET_INCOME_TREND_PROMPT \
        .replace("<document>", combined_text) \
        .replace("<year>", str(year)) \
        .replace("<year_minus_1>", str(prev_year)) \
        .replace("<year_minus_2>", str(prev_year_2)) \
        .replace("<net_income_y1>", net_income_y1) \
        .replace("<net_income_y2>", net_income_y2) \
        .replace("<net_income_y3>", net_income_y3) \
        .replace("<company_name>", company_name)

    return run_llm_prompt(prompt)

def extract_ebitda_margin(folder_name, year, company_name):
    combined_text = load_combined_text(folder_name, "ebitda_margin")
    if not combined_text:
        return ""
    prompt = EXTRACT_EBITDA_MARGIN_PROMPT.replace("<document>", combined_text).replace("<year>", str(year)).replace("<company_name>", company_name)
    return run_llm_prompt(prompt)

def extract_operating_expense_commentary(folder_name, year, operating_expenses, company_name):
    combined_text = load_combined_text(folder_name, "operating_expense_commentary")
    if not combined_text:
        return ""
    prompt = EXTRACT_OPERATING_EXPENSE_COMMENTARY_PROMPT \
        .replace("<document>", combined_text) \
        .replace("<year>", str(year)) \
        .replace("<operating_expenses>", str(operating_expenses or "N/A")) \
        .replace("<company_name>", company_name)
    return run_llm_prompt(prompt)

def extract_valuation_commentary(
    folder_name,
    year,
    total_revenue,
    net_income,
    operating_income,
    sales_and_marketing_expense,
    eps,
    total_assets,
    stock_issuance,
    stock_repurchases, company_name
):
    combined_text = load_combined_text(folder_name, "valuation_commentary")
    if not combined_text:
        return ""
    prompt = EXTRACT_VALUATION_COMMENTARY_PROMPT \
        .replace("<document>", combined_text) \
        .replace("<year>", str(year)) \
        .replace("<total_net_sales>", str(total_revenue or "N/A")) \
        .replace("<net_income>", str(net_income or "N/A")) \
        .replace("<operating_income>", str(operating_income or "N/A")) \
        .replace("<sales_and_marketing_expense>", str(sales_and_marketing_expense or "N/A")) \
        .replace("<eps>", str(eps or "N/A")) \
        .replace("<total_assets>", str(total_assets or "N/A")) \
        .replace("<stock_issuance>", str(stock_issuance or "N/A")) \
        .replace("<stock_repurchases>", str(stock_repurchases or "N/A")) \
        .replace("<company_name>", company_name)
    return run_llm_prompt(prompt)

def extract_capital_expenditures_projects(folder_name, year, capital_expenditures, company_name):
    combined_text = load_combined_text(folder_name, "capital_expenditures_projects")
    if not combined_text:
        return ""
    prompt = EXTRACT_CAPEX_PROJECTS_PROMPT \
        .replace("<document>", combined_text) \
        .replace("<year>", str(year)) \
        .replace("<capital_expenditures>", str(capital_expenditures or "N/A")) \
        .replace("<company_name>", company_name)
    return run_llm_prompt(prompt)

def extract_dividend_and_buyback_policy(folder_name, year, company_name, dividends_paid, stock_repurchases, stock_issuance):
    combined_text = load_combined_text(folder_name, "dividend_and_buyback_policy")
    if not combined_text:
        return ""
    prompt = EXTRACT_DIVIDEND_AND_BUYBACK_POLICY_PROMPT \
        .replace("<document>", combined_text) \
        .replace("<year>", str(year)) \
        .replace("<company_name>", company_name) \
        .replace("<dividends_paid>", str(dividends_paid or "N/A")) \
        .replace("<stock_repurchases>", str(stock_repurchases or "N/A")) \
        .replace("<stock_issuance>", str(stock_issuance or "N/A"))
    return run_llm_prompt(prompt)

def extract_working_capital_efficiency(folder_name, year, company_name, days_sales_outstanding):
    combined_text = load_combined_text(folder_name, "working_capital_efficiency")
    if not combined_text:
        return ""
    prompt = EXTRACT_WORKING_CAPITAL_EFFICIENCY_PROMPT \
        .replace("<document>", combined_text) \
        .replace("<year>", str(year)) \
        .replace("<company_name>", company_name) \
        .replace("<days_sales_outstanding>", str(days_sales_outstanding or "N/A"))
    return run_llm_prompt(prompt)

def extract_management_changes(folder_name, year, company_name):
    combined_text = load_combined_text(folder_name, "management_changes")
    if not combined_text:
        return ""
    prompt = EXTRACT_MANAGEMENT_CHANGES_PROMPT \
        .replace("<document>", combined_text) \
        .replace("<year>", str(year)) \
        .replace("<company_name>", company_name)
    return run_llm_prompt(prompt)

def extract_supply_chain_disruptions(folder_name, year, company_name):
    combined_text = load_combined_text(folder_name, "supply_chain_disruptions")
    if not combined_text:
        return ""
    prompt = EXTRACT_SUPPLY_CHAIN_DISRUPTIONS_PROMPT \
        .replace("<document>", combined_text) \
        .replace("<year>", str(year)) \
        .replace("<company_name>", company_name)
    return run_llm_prompt(prompt)

def extract_esg_initiatives(folder_name, year, company_name):
    combined_text = load_combined_text(folder_name, "esg_initiatives")
    if not combined_text:
        return ""
    prompt = EXTRACT_ESG_INITIATIVES_PROMPT \
        .replace("<document>", combined_text) \
        .replace("<year>", str(year)) \
        .replace("<company_name>", company_name)
    return run_llm_prompt(prompt)

def extract_esg_controversies(folder_name, year, company_name):
    combined_text = load_combined_text(folder_name, "esg_controversies")
    if not combined_text:
        return ""
    prompt = EXTRACT_ESG_CONTROVERSIES_PROMPT \
        .replace("<document>", combined_text) \
        .replace("<year>", str(year)) \
        .replace("<company_name>", company_name)
    return run_llm_prompt(prompt)

def extract_governance_structure(folder_name, year, company_name):
    combined_text = load_combined_text(folder_name, "governance_structure")
    if not combined_text:
        return ""
    prompt = EXTRACT_GOVERNANCE_STRUCTURE_PROMPT \
        .replace("<document>", combined_text) \
        .replace("<year>", str(year)) \
        .replace("<company_name>", company_name)
    return run_llm_prompt(prompt)

def extract_debt_sustainability_commentary(folder_name, year, company_name, debt_to_equity_ratio):
    combined_text = load_combined_text(folder_name, "debt_sustainability_commentary")
    if not combined_text:
        return ""
    prompt = EXTRACT_DEBT_SUSTAINABILITY_COMMENTARY_PROMPT \
        .replace("<document>", combined_text) \
        .replace("<year>", str(year)) \
        .replace("<company_name>", company_name) \
        .replace("<debt_to_equity_ratio>", str(debt_to_equity_ratio or "N/A"))
    return run_llm_prompt(prompt)


def extract_debt_refinancing_activity(folder_name, year, company_name):
    combined_text = load_combined_text(folder_name, "debt_refinancing_activity")
    if not combined_text:
        return ""
    prompt = EXTRACT_DEBT_REFINANCING_ACTIVITY_PROMPT \
        .replace("<document>", combined_text) \
        .replace("<year>", str(year)) \
        .replace("<company_name>", company_name)
    return run_llm_prompt(prompt)

def extract_technology_impact_on_operations(folder_name, year, company_name):
    combined_text = load_combined_text(folder_name, "technology_impact_on_operations")
    if not combined_text:
        return ""
    prompt = EXTRACT_TECHNOLOGY_IMPACT_ON_OPERATIONS_PROMPT \
        .replace("<document>", combined_text) \
        .replace("<year>", str(year)) \
        .replace("<company_name>", company_name)
    return run_llm_prompt(prompt)

def extract_emerging_tech_investments(folder_name, company_name):
    combined_text = load_combined_text(folder_name, "emerging_tech_investments")
    if not combined_text:
        return ""
    prompt = EXTRACT_EMERGING_TECH_INVESTMENTS_PROMPT \
        .replace("<document>", combined_text) \
        .replace("<company_name>", company_name)
    return run_llm_prompt(prompt)

def extract_intellectual_property_assets(folder_name, year, company_name):
    combined_text = load_combined_text(folder_name, "intellectual_property_assets")
    if not combined_text:
        return ""
    prompt = EXTRACT_IP_ASSETS_PROMPT \
        .replace("<document>", combined_text) \
        .replace("<year>", str(year)) \
        .replace("<company_name>", company_name)
    return run_llm_prompt(prompt)

def extract_research_and_development_commentary(folder_name, year, company_name, research_and_development_expense, research_and_development_investment):
    combined_text = load_combined_text(folder_name, "research_and_development_commentary")
    if not combined_text:
        return ""
    prompt = EXTRACT_R_AND_D_COMMENTARY_PROMPT \
        .replace("<document>", combined_text) \
        .replace("<year>", str(year)) \
        .replace("<company_name>", company_name) \
        .replace("<rd_expense>", str(research_and_development_expense or "N/A")) \
        .replace("<rd_investment>", str(research_and_development_investment or "N/A"))
    return run_llm_prompt(prompt)

def extract_brand_positioning(folder_name, year, company_name):
    combined_text = load_combined_text(folder_name, "brand_positioning")
    if not combined_text:
        return ""
    prompt = EXTRACT_BRAND_POSITIONING_PROMPT \
        .replace("<document>", combined_text) \
        .replace("<year>", str(year)) \
        .replace("<company_name>", company_name)
    return run_llm_prompt(prompt)

def extract_rebranding_or_marketing_shift(folder_name, year, company_name):
    combined_text = load_combined_text(folder_name, "rebranding_or_marketing_shift")
    if not combined_text:
        return ""
    prompt = EXTRACT_REBRANDING_OR_MARKETING_SHIFT_PROMPT \
        .replace("<document>", combined_text) \
        .replace("<year>", str(year)) \
        .replace("<company_name>", company_name)
    return run_llm_prompt(prompt)

def extract_macroeconomic_sensitivity(folder_name, year, company_name, foreign_revenue_percent):
    combined_text = load_combined_text(folder_name, "macroeconomic_sensitivity")
    if not combined_text:
        return ""
    prompt = EXTRACT_MACROECONOMIC_SENSITIVITY_PROMPT \
        .replace("<document>", combined_text) \
        .replace("<year>", str(year)) \
        .replace("<company_name>", company_name) \
        .replace("<foreign_revenue_percent>", str(foreign_revenue_percent or "N/A"))
    return run_llm_prompt(prompt)

def extract_geopolitical_and_economic_impacts(folder_name, year, company_name):
    combined_text = load_combined_text(folder_name, "geopolitical_and_economic_impacts")
    if not combined_text:
        return ""
    prompt = EXTRACT_GEOPOLITICAL_AND_ECONOMIC_IMPACTS_PROMPT \
        .replace("<document>", combined_text) \
        .replace("<year>", str(year)) \
        .replace("<company_name>", company_name)
    return run_llm_prompt(prompt)

def extract_growth_scenarios(
        folder_name, year, company_name,
        total_revenue, net_income, operating_income,
        research_and_development_expense, capital_expenditures,
        stock_repurchases, foreign_revenue_percent,
        growth_strategy, macroeconomic_sensitivity,
        emerging_tech_investments, valuation_commentary, operating_expense_commentary
):
    combined_text = load_combined_text(folder_name, "growth_strategy")
    if not combined_text:
        return ""

    prompt = EXTRACT_GROWTH_SCENARIOS_PROMPT \
        .replace("<document>", combined_text) \
        .replace("<year>", str(year)) \
        .replace("<company_name>", company_name) \
        .replace("<total_revenue>", str(total_revenue or "N/A")) \
        .replace("<net_income>", str(net_income or "N/A")) \
        .replace("<operating_income>", str(operating_income or "N/A")) \
        .replace("<research_and_development_expense>", str(research_and_development_expense or "N/A")) \
        .replace("<capital_expenditures>", str(capital_expenditures or "N/A")) \
        .replace("<stock_repurchases>", str(stock_repurchases or "N/A")) \
        .replace("<foreign_revenue_percent>", str(foreign_revenue_percent or "N/A")) \
        .replace("<growth_strategy>", growth_strategy or "N/A") \
        .replace("<macroeconomic_sensitivity>", macroeconomic_sensitivity or "N/A") \
        .replace("<emerging_tech_investments>", emerging_tech_investments or "N/A") \
        .replace("<valuation_commentary>", valuation_commentary or "N/A") \
        .replace("<operating_expense_commentary>", operating_expense_commentary or "N/A")

    return run_llm_prompt(prompt)

def extract_forward_looking_statement(folder_name, year, company_name):
    combined_text = load_combined_text(folder_name, "forward-looking_statement")
    if not combined_text:
        return ""
    prompt = EXTRACT_FORWARD_LOOKING_STATEMENT_PROMPT \
        .replace("<document>", combined_text) \
        .replace("<year>", str(year)) \
        .replace("<company_name>", company_name)
    return run_llm_prompt(prompt)
