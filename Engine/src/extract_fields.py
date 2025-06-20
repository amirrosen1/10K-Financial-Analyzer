import os
os.environ["HF_HOME"] = "/cs/ep/110/HUJI-project/hf_cache"
os.environ["TRITON_CACHE_DIR"] = "/cs/ep/110/HUJI-project/hf_cache/triton_cache"
os.environ["TRANSFORMERS_CACHE"] = "/cs/ep/110/HUJI-project/hf_cache"
os.environ["HF_DATASETS_CACHE"] = "/cs/ep/110/HUJI-project/hf_cache"
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

import ctypes
import platform
import pandas as pd
from Engine.src.llm_user_query import *
from tqdm import tqdm
import re
import google.protobuf
from google.protobuf import message
import json



# ----------------------------
# Helper Function for Windows Paths
# ----------------------------
def get_short_path(long_path):
    if platform.system() == "Windows":
        buffer = ctypes.create_unicode_buffer(260)  # MAX_PATH
        result = ctypes.windll.kernel32.GetShortPathNameW(long_path, buffer, 260)
        if result:
            return buffer.value
    return long_path

def clean_sector_output(output):
    # Remove Markdown/code block syntax and XML-like tags
    output = re.sub(r"[`<>]", "", output)
    output = re.sub(r"\s+", " ", output)
    return output.strip()


def extract_numeric_value(value: str):
    if not isinstance(value, str):
        print("[Debug] Input is not a string:", type(value))
        return None

    print("[Debug] Raw input:", value)
    value = value.lower().strip()

    # Remove common prefixes and code blocks
    value = re.sub(r"^(answer|response|return|output|explanation|note)[:\-\s]+", "", value)
    value = value.split("```")[0].strip()
    print("[Debug] Cleaned input:", value)

    if value in {"n/a", "na", "none", ""}:
        print("[Debug] Value is empty or NA")
        return None

    math_match = re.search(r'([\d,.]+)\s*[-–]\s*([\d,.]+)\s*=\s*([\d,.]+)', value)
    if math_match:
        try:
            a, b, result = [float(x.replace(',', '')) for x in math_match.groups()]
            print("[Debug] Math expression found:", a, "-", b, "=", result)
            return result
        except Exception:
            print("[Debug] Failed parsing math expression")
            pass

    matches = re.findall(r"(\$?\s?\d[\d,]*(?:\.\d+)?)(?:\s*(million|billion|m|b))?", value)
    print(f"[Debug] Matches found: {matches}")

    candidates = []
    for num_str, scale in matches:
        try:
            if any(kw in value for kw in ["end of period", "ending balance", "end of year"]):
                print("[Debug] Skipping due to ending keyword")
                continue

            num_str_clean = num_str.replace("$", "").replace(",", "").strip()
            number = float(num_str_clean)

            if 2000 <= number <= 2100:
                print(f"[Debug] Skipping likely year: {number} (with scale: {scale})")
                continue

            # Apply scale if explicitly present
            if scale:
                if scale in {"million", "m"}:
                    print(f"[Debug] Scaling {number} by 1M")
                    number *= 1_000_000
                elif scale in {"billion", "b"}:
                    print(f"[Debug] Scaling {number} by 1B")
                    number *= 1_000_000_000

            print(f"[Debug] Candidate extracted: {number}")
            candidates.append(number)
        except Exception as e:
            print(f"[Debug] Failed to parse '{num_str}' with scale '{scale}':", e)
            continue

    final = max(candidates) if candidates else None
    print("[Debug] Final extracted value:", final)
    return final


def extract_and_scale_numeric_value(raw_value: str, field_name: str) -> float:
    value = extract_numeric_value(raw_value)

    MILLION_FIELDS = {
        "total_revenue", "net_income", "operating_income", "gross_profit",
        "cash_flow_operating_activities", "capital_expenditures", "total_assets",
        "total_liabilities", "sales_and_marketing_expense", "sg_a_expense",
        "stock_issuance", "stock_repurchases", "operating_expenses", "dividends_paid",
        "accounts_receivable", "shareholder_equity", "research_and_development_expense",
        "research_and_development_investment", "foreign_revenue"
    }

    if field_name in MILLION_FIELDS and value is not None:
        if value < 10_000_000:  # value seems unscaled (e.g., 40,000 = $40M)
            print(f"[Debug] Scaling {field_name} value to millions: {value} → {value * 1_000_000}")
            value *= 1_000_000

    return value


def extract_filing_year_from_response(response):
    if isinstance(response, int):
        print(f"[Debug] Direct year (int): {response}")
        return response if 2000 <= response <= 2100 else None

    if not isinstance(response, str):
        print(f"[Error] Invalid response type: {type(response)}")
        return None

    response = response.strip().lower()
    match = re.search(r"\b(20\d{2})\b", response)
    if match:
        print(f"[Debug] Extracted year from string: {match.group(1)}")
        return int(match.group(1))

    print(f"[Error] No year found in response: {response}")
    return None


def extract_metadata_table_only_name_year(query_results_dir,company_tickers) -> pd.DataFrame:
    rows = []
    folder_list = [f for f in os.listdir(query_results_dir) if os.path.isdir(os.path.join(query_results_dir, f))]

    for folder_name in tqdm(folder_list, desc="Extracting company + year"):
        folder_path = os.path.join(query_results_dir, folder_name)

        try:
            extracted_name = extract_company_name(folder_name)
            print("[Debug] Company name extracted:", extracted_name)
            company_name,cik = match_company_name_to_cik(extracted_name,company_tickers)
        except Exception as e:
            print(f"[Error] Company name failed for {folder_name}: {e}")
            company_name = ""
            cik = ""

        try:
            raw_year = extract_filing_year(folder_name)
            print("[Debug] Year extracted:", raw_year)
            year = extract_filing_year_from_response(raw_year)
            print("[Debug] Year after numeric extraction update code:", year)
        except Exception as e:
            print(f"[Error] Filing year failed for {folder_name}: {e}")
            year = None

        except Exception as e:
            print(f"[Error] Company/Year extraction failed for {folder_name}: {e}")
            company_name, year = None, None

        rows.append({
            "folder_name": folder_name,
            "company_name": company_name,
            "year": year,
            "cik":cik
        })
    return pd.DataFrame(rows)


# ----------------------------
# Function: Extract Metadata Table
# ----------------------------
def extract_metadata_table(query_results_dir,company_tickers) -> pd.DataFrame:

    # Load previously saved results to enable resuming
    output_file_path = os.path.join(query_results_dir, "..", "final_metadata_table.csv")
    if os.path.exists(output_file_path):
        existing_df = pd.read_csv(output_file_path)
        processed_folders = set(existing_df["folder_name"].tolist())
        rows = existing_df.to_dict(orient="records")  # So we continue from the previous rows
        print(f"[Resume] Loaded {len(processed_folders)} previously processed documents.")
    else:
        processed_folders = set()
        rows = []

    folder_list = [f for f in os.listdir(query_results_dir) if os.path.isdir(os.path.join(query_results_dir, f))]

    for folder_name in tqdm(folder_list, desc="Extracting company + year"):

        if folder_name in processed_folders:
            print(f"[Skip] Already processed: {folder_name}")
            continue

        try:
            extracted_name = extract_company_name(folder_name)
            print("[Debug] Company name extracted:", extracted_name)
            company_name,cik = match_company_name_to_cik(extracted_name,company_tickers)
        except Exception as e:
            print(f"[Error] Company name failed for {folder_name}: {e}")
            company_name = ""
            cik = ""

        try:
            raw_year = extract_filing_year(folder_name)
            print("[Debug] Year extracted:", raw_year)
            year = extract_filing_year_from_response(raw_year)
            print("[Debug] Year after numeric extraction update code:", year)
        except Exception as e:
            print(f"[Error] Filing year failed for {folder_name}: {e}")
            year = None

        except Exception as e:
            print(f"[Error] Company/Year extraction failed for {folder_name}: {e}")
            company_name, year = None, None

        try:
            sector = extract_sector(folder_name)
            sector = clean_sector_output(sector)
        except Exception as e:
            print(f"[Error] Sector extraction failed for {folder_name}: {e}")
            sector = None

        try:
            total_revenue = extract_total_revenue(folder_name, year)
            print("[Debug] Total Revenue extracted:", total_revenue)

            total_revenue = extract_and_scale_numeric_value(total_revenue, "total_revenue")
            print("[Debug] Total Revenue after numeric extraction:", total_revenue)

        except Exception as e:
            print(f"[Error] Total Revenue extraction failed for {folder_name}: {e}")
            total_revenue = None

        try:
            net_income = extract_net_income(folder_name, year)
            print("[Debug] Net Income extracted:", net_income)

            net_income = extract_and_scale_numeric_value(net_income, "net_income")
            print("[Debug] Net Income after numeric extraction:", net_income)

        except Exception as e:
            print(f"[Error] Net Income extraction failed for {folder_name}: {e}")
            net_income = None

        try:
            eps = extract_eps(folder_name, year)
            print("[Debug] EPS extracted:", eps)

            eps = extract_numeric_value(eps)
            print("[Debug] EPS after numeric extraction:", eps)

        except Exception as e:
            print(f"[Error] EPS extraction failed for {folder_name}: {e}")
            eps = None

        try:
            operating_income = extract_operating_income(folder_name, year)
            print("[Debug] Operating Income extracted:", operating_income)

            operating_income = extract_and_scale_numeric_value(operating_income, "operating_income")
            print("[Debug] Operating Income after numeric extraction:", operating_income)

        except Exception as e:
            print(f"[Error] Operating Income extraction failed for {folder_name}: {e}")
            operating_income = None

        try:
            gross_profit = extract_gross_profit(folder_name, year)
            print("[Debug] Gross Profit extracted:", gross_profit)

            gross_profit = extract_and_scale_numeric_value(gross_profit, "gross_profit")
            print("[Debug] Gross Profit after numeric extraction:", gross_profit)

        except Exception as e:
            print(f"[Error] Gross Profit extraction failed for {folder_name}: {e}")
            gross_profit = None

        try:
            cash_flow = extract_cash_flow_operating_activities(folder_name, year)
            print("[Debug] Cash Flow from Operating Activities extracted:", cash_flow)

            cash_flow = extract_and_scale_numeric_value(cash_flow, "cash_flow_operating_activities")
            print("[Debug] Cash Flow from Operating Activities after numeric extraction:", cash_flow)

        except Exception as e:
            print(f"[Error] Cash Flow from Operating Activities extraction failed for {folder_name}: {e}")
            cash_flow = None

        try:
            capex = extract_capital_expenditures(folder_name, year)
            print("[Debug] Capital Expenditures extracted:", capex)

            capex = extract_and_scale_numeric_value(capex, "capital_expenditures")
            print("[Debug] Capital Expenditures after numeric extraction:", capex)

        except Exception as e:
            print(f"[Error] Capital Expenditures extraction failed for {folder_name}: {e}")
            capex = None

        try:
            total_assets = extract_total_assets(folder_name, year)
            print("[Debug] Total Assets extracted:", total_assets)

            total_assets = extract_and_scale_numeric_value(total_assets, "total_assets")
            print("[Debug] Total Assets after numeric extraction:", total_assets)

        except Exception as e:
            print(f"[Error] Total Assets extraction failed for {folder_name}: {e}")
            total_assets = None

        try:
            total_liabilities = extract_total_liabilities(folder_name, year)
            print("[Debug] Total Liabilities extracted:", total_liabilities)

            total_liabilities = extract_and_scale_numeric_value(total_liabilities, "total_liabilities")
            print("[Debug] Total Liabilities after numeric extraction:", total_liabilities)

        except Exception as e:
            print(f"[Error] Total Liabilities extraction failed for {folder_name}: {e}")
            total_liabilities = None

        try:
            sales_marketing = extract_sales_and_marketing_expense(folder_name, year)
            print("[Debug] Sales & Marketing Expense extracted:", sales_marketing)

            sales_marketing = extract_and_scale_numeric_value(sales_marketing, "sales_and_marketing_expense")
            print("[Debug] Sales & Marketing Expense after numeric extraction:", sales_marketing)

        except Exception as e:
            print(f"[Error] Sales & Marketing Expense extraction failed for {folder_name}: {e}")
            sales_marketing = None
        try:
            sg_a_expense = extract_sg_a_expense(folder_name, year)
            print("[Debug] SG&A Expense extracted:", sg_a_expense)

            sg_a_expense = extract_and_scale_numeric_value(sg_a_expense, "sg_a_expense")
            print("[Debug] SG&A Expense after numeric extraction:", sg_a_expense)

            # Fallback logic if SG&A is missing
            if sg_a_expense is None:
                print("[Fallback] SG&A not found — attempting to compute from components.")

                general_admin = extract_general_and_administrative_expense(folder_name, year)
                general_admin = extract_numeric_value(general_admin)
                print("[Fallback] General & Administrative extracted:", general_admin)

                if sales_marketing and general_admin:
                    sg_a_expense = sales_marketing + general_admin
                    print("[Fallback] SG&A estimated as S&M + G&A:", sg_a_expense)

        except Exception as e:
            print(f"[Error] SG&A Expense extraction failed for {folder_name}: {e}")
            sg_a_expense = None

        try:
            stock_issuance = extract_stock_issuance(folder_name, year)
            print("[Debug] Stock Issuance extracted:", stock_issuance)

            stock_issuance = extract_and_scale_numeric_value(stock_issuance, "stock_issuance")
            print("[Debug] Stock Issuance after numeric extraction:", stock_issuance)

        except Exception as e:
            print(f"[Error] Stock Issuance extraction failed for {folder_name}: {e}")
            stock_issuance = None

        try:
            stock_repurchases = extract_stock_repurchases(folder_name, year)
            print("[Debug] Stock Repurchases extracted:", stock_repurchases)

            stock_repurchases = extract_and_scale_numeric_value(stock_repurchases, "stock_repurchases")
            print("[Debug] Stock Repurchases after numeric extraction:", stock_repurchases)
        except Exception as e:
            print(f"[Error] Stock Repurchases extraction failed for {folder_name}: {e}")
            stock_repurchases = None

        try:
            fiscal_year_end = extract_fiscal_year_end(folder_name, year)
            print("[Debug] Fiscal Year End extracted:", fiscal_year_end)

        except Exception as e:
            print(f"[Error] Fiscal Year End extraction failed for {folder_name}: {e}")
            fiscal_year_end = None

        try:
            operating_expenses = extract_operating_expenses(folder_name, year)
            print("[Debug] Operating Expenses extracted:", operating_expenses)

            operating_expenses = extract_and_scale_numeric_value(operating_expenses, "operating_expenses")
            print("[Debug] Operating Expenses after numeric extraction:", operating_expenses)

        except Exception as e:
            print(f"[Error] Operating Expenses extraction failed for {folder_name}: {e}")
            operating_expenses = None

        try:
            dividends_paid = extract_dividends_paid(folder_name, year)
            print("[Debug] Dividends Paid extracted:", dividends_paid)

            dividends_paid = extract_and_scale_numeric_value(dividends_paid, "dividends_paid")
            print("[Debug] Dividends Paid after numeric extraction:", dividends_paid)

        except Exception as e:
            print(f"[Error] Dividends Paid extraction failed for {folder_name}: {e}")
            dividends_paid = None

        try:
            accounts_receivable = extract_accounts_receivable(folder_name, year)
            print("[Debug] Accounts Receivable extracted:", accounts_receivable)

            accounts_receivable = extract_and_scale_numeric_value(accounts_receivable, "accounts_receivable")
            print("[Debug] Accounts Receivable after numeric extraction:", accounts_receivable)

        except Exception as e:
            print(f"[Error] Accounts Receivable extraction failed for {folder_name}: {e}")
            accounts_receivable = None

        try:
            shareholder_equity = extract_shareholder_equity(folder_name, year)
            print("[Debug] Shareholder Equity extracted:", shareholder_equity)

            shareholder_equity = extract_and_scale_numeric_value(shareholder_equity, "shareholder_equity")
            print("[Debug] Shareholder Equity after numeric extraction:", shareholder_equity)

        except Exception as e:
            print(f"[Error] Shareholder Equity extraction failed for {folder_name}: {e}")
            shareholder_equity = None

        try:
            research_and_development_expense = extract_research_and_development_expense(folder_name, year)
            print("[Debug] R&D Expense extracted:", research_and_development_expense)

            research_and_development_expense = extract_and_scale_numeric_value(research_and_development_expense, "research_and_development_expense")
            print("[Debug] R&D Expense after numeric extraction:", research_and_development_expense)
        except Exception as e:
            print(f"[Error] R&D Expense extraction failed for {folder_name}: {e}")
            research_and_development_expense = None

        try:
            research_and_development_investment = extract_research_and_development_investment(folder_name, year)
            print("[Debug] R&D Investment extracted:", research_and_development_investment)

            research_and_development_investment = extract_and_scale_numeric_value(research_and_development_investment, "research_and_development_investment")
            print("[Debug] R&D Investment after numeric extraction:", research_and_development_investment)
        except Exception as e:
            print(f"[Error] R&D Investment extraction failed for {folder_name}: {e}")
            research_and_development_investment = None

        try:
            foreign_revenue = extract_foreign_revenue(folder_name, year)
            print("[Debug] Foreign Revenue extracted:", foreign_revenue)

            foreign_revenue = extract_and_scale_numeric_value(foreign_revenue, "foreign_revenue")
            print("[Debug] Foreign Revenue after numeric extraction:", foreign_revenue)
        except Exception as e:
            print(f"[Error] Foreign Revenue extraction failed for {folder_name}: {e}")
            foreign_revenue = None

        # -------------------------------
        # Derived Calculated Fields
        # -------------------------------

        try:
            days_sales_outstanding = ((accounts_receivable) / (total_revenue)) * 365 \
                if accounts_receivable and total_revenue else None
        except Exception as e:
            print(f"[Error] Failed to calculate DSO for {folder_name}: {e}")
            days_sales_outstanding = None

        try:
            debt_to_equity_ratio = (total_liabilities) / (shareholder_equity) \
                if total_liabilities and shareholder_equity else None
        except Exception as e:
            print(f"[Error] Failed to calculate Debt-to-Equity Ratio for {folder_name}: {e}")
            debt_to_equity_ratio = None

        try:
            foreign_revenue_percent = ((foreign_revenue) / (total_revenue)) * 100 \
                if foreign_revenue and total_revenue else None
        except Exception as e:
            print(f"[Error] Failed to calculate Foreign Revenue % for {folder_name}: {e}")
            foreign_revenue_percent = None

        try:
            revenue_streams_summary = extract_revenue_streams_summary(folder_name, year, company_name)
        except Exception as e:
            print(f"[Error] Revenue Streams Summary extraction failed for {folder_name}: {e}")
            revenue_streams_summary = None

        try:
            customer_base = extract_customer_base(folder_name, year, company_name)
        except Exception as e:
            print(f"[Error] Customer Base extraction failed for {folder_name}: {e}")
            customer_base = None

        try:
            competitive_landscape = extract_competitive_landscape(folder_name, year, company_name)
        except Exception as e:
            print(f"[Error] Competitive Landscape extraction failed for {folder_name}: {e}")
            competitive_landscape = None

        try:
            growth_strategy = extract_growth_strategy(folder_name, year, company_name)
        except Exception as e:
            print(f"[Error] Growth Strategy extraction failed for {folder_name}: {e}")
            growth_strategy = None

        try:
            highlighted_risks = extract_highlighted_risks(folder_name, year, company_name)
        except Exception as e:
            print(f"[Error] Highlighted Risks extraction failed for {folder_name}: {e}")
            highlighted_risks = None

        try:
            regulatory_challenges = extract_regulatory_challenges(folder_name, year, company_name)
        except Exception as e:
            print(f"[Error] Regulatory Challenges extraction failed for {folder_name}: {e}")
            regulatory_challenges = None

        try:
            net_income_trend_summary = extract_net_income_trend_summary(
                folder_name, year, company_name, net_income
            )
        except Exception as e:
            print(f"[Error] Net Income Trend Summary extraction failed for {folder_name}: {e}")
            net_income_trend_summary = None

        try:
            ebitda_margin = extract_ebitda_margin(folder_name, year, company_name)
        except Exception as e:
            print(f"[Error] Ebitda Margin extraction failed for {folder_name}: {e}")
            ebitda_margin = None

        try:
            operating_expense_commentary = extract_operating_expense_commentary(folder_name, year, operating_expenses, company_name)
        except Exception as e:
            print(f"[Error] Operating Expense Commentary extraction failed for {folder_name}: {e}")
            operating_expense_commentary = None

        try:
            valuation_commentary = extract_valuation_commentary(
                folder_name, year, total_revenue, net_income, operating_income,
                sales_marketing, eps, total_assets, stock_issuance, stock_repurchases, company_name
            )
        except Exception as e:
            print(f"[Error] Valuation Commentary extraction failed for {folder_name}: {e}")
            valuation_commentary = None

        try:
            capex_projects = extract_capital_expenditures_projects(folder_name, year, capex, company_name)
        except Exception as e:
            print(f"[Error] Capital Expenditure Projects extraction failed for {folder_name}: {e}")
            capex_projects = None

        try:
            dividend_and_buyback_policy = extract_dividend_and_buyback_policy(
                folder_name, year, company_name, dividends_paid, stock_repurchases, stock_issuance
            )
        except Exception as e:
            print(f"[Error] Dividend and Buyback Policy extraction failed for {folder_name}: {e}")
            dividend_and_buyback_policy = None

        try:
            working_capital_efficiency = extract_working_capital_efficiency(folder_name, year, company_name,
                                                                            days_sales_outstanding)
        except Exception as e:
            print(f"[Error] Working Capital Efficiency extraction failed for {folder_name}: {e}")
            working_capital_efficiency = None

        try:
            management_changes = extract_management_changes(folder_name, year, company_name)
        except Exception as e:
            print(f"[Error] Management Changes extraction failed for {folder_name}: {e}")
            management_changes = None

        try:
            supply_chain_disruptions = extract_supply_chain_disruptions(folder_name, year, company_name)
        except Exception as e:
            print(f"[Error] Supply Chain Disruptions extraction failed for {folder_name}: {e}")
            supply_chain_disruptions = None

        try:
            esg_initiatives = extract_esg_initiatives(folder_name, year, company_name)
        except Exception as e:
            print(f"[Error] ESG Initiatives extraction failed for {folder_name}: {e}")
            esg_initiatives = None

        try:
            esg_controversies = extract_esg_controversies(folder_name, year, company_name)
        except Exception as e:
            print(f"[Error] ESG Controversies extraction failed for {folder_name}: {e}")
            esg_controversies = None

        try:
            governance_structure = extract_governance_structure(folder_name, year, company_name)
        except Exception as e:
            print(f"[Error] Governance Structure extraction failed for {folder_name}: {e}")
            governance_structure = None

        try:
            debt_sustainability_commentary = extract_debt_sustainability_commentary(folder_name, year, company_name,
                                                                                    debt_to_equity_ratio)
        except Exception as e:
            print(f"[Error] Debt Sustainability Commentary extraction failed for {folder_name}: {e}")
            debt_sustainability_commentary = None

        try:
            debt_refinancing_activity = extract_debt_refinancing_activity(folder_name, year, company_name)
        except Exception as e:
            print(f"[Error] Debt Refinancing Activity extraction failed for {folder_name}: {e}")
            debt_refinancing_activity = None

        try:
            technology_impact_on_operations = extract_technology_impact_on_operations(folder_name, year, company_name)
        except Exception as e:
            print(f"[Error] Technology Impact on Operations extraction failed for {folder_name}: {e}")
            technology_impact_on_operations = None

        try:
            emerging_tech_investments = extract_emerging_tech_investments(folder_name, company_name)
        except Exception as e:
            print(f"[Error] Emerging Tech Investments extraction failed for {folder_name}: {e}")
            emerging_tech_investments = None

        try:
            intellectual_property_assets = extract_intellectual_property_assets(folder_name, year, company_name)
        except Exception as e:
            print(f"[Error] Intellectual Property Assets extraction failed for {folder_name}: {e}")
            intellectual_property_assets = None

        try:
            research_and_development_commentary = extract_research_and_development_commentary(
                folder_name, year, company_name, research_and_development_expense, research_and_development_investment)
        except Exception as e:
            print(f"[Error] R&D Commentary extraction failed for {folder_name}: {e}")
            research_and_development_commentary = None

        try:
            brand_positioning = extract_brand_positioning(folder_name, year, company_name)
        except Exception as e:
            print(f"[Error] Brand Positioning extraction failed for {folder_name}: {e}")
            brand_positioning = None

        try:
            rebranding_or_marketing_shift = extract_rebranding_or_marketing_shift(folder_name, year, company_name)
        except Exception as e:
            print(f"[Error] Rebranding or Marketing Shift extraction failed for {folder_name}: {e}")
            rebranding_or_marketing_shift = None

        try:
            macroeconomic_sensitivity = extract_macroeconomic_sensitivity(
                folder_name, year, company_name, foreign_revenue_percent)
        except Exception as e:
            print(f"[Error] Macroeconomic Sensitivity extraction failed for {folder_name}: {e}")
            macroeconomic_sensitivity = None

        try:
            geopolitical_and_economic_impacts = extract_geopolitical_and_economic_impacts(folder_name, year,
                                                                                          company_name)
        except Exception as e:
            print(f"[Error] Geopolitical and Economic Impacts extraction failed for {folder_name}: {e}")
            geopolitical_and_economic_impacts = None

        try:
            growth_scenarios = extract_growth_scenarios(
                folder_name, year, company_name,
                total_revenue, net_income, operating_income,
                research_and_development_expense, capex,
                stock_repurchases, foreign_revenue_percent,
                growth_strategy, macroeconomic_sensitivity,
                emerging_tech_investments, valuation_commentary, operating_expense_commentary
            )
        except Exception as e:
            print(f"[Error] Growth Scenarios extraction failed for {folder_name}: {e}")
            growth_scenarios = None

        try:
            forward_looking_statement = extract_forward_looking_statement(folder_name, year, company_name)
        except Exception as e:
            print(f"[Error] Forward-Looking Statement extraction failed for {folder_name}: {e}")
            forward_looking_statement = None


        rows.append({
            "folder_name": folder_name,
            "company_name": company_name,
            "cik": cik,
            "year": year,
            "sector": sector,
            "total_revenue": total_revenue,
            "net_income": net_income,
            "earnings_per_share": eps,
            "operating_income": operating_income,
            "gross_profit": gross_profit,
            "cash_flow_operating_activities": cash_flow,
            "capital_expenditures": capex,
            "total_assets": total_assets,
            "total_liabilities": total_liabilities,
            "sales_and_marketing_expense": sales_marketing,
            "sg_a_expense": sg_a_expense,
            "stock_issuance": stock_issuance,
            "stock_repurchases": stock_repurchases,
            "fiscal_year_end": fiscal_year_end,
            "operating_expenses": operating_expenses,
            "dividends_paid": dividends_paid,
            "accounts_receivable": accounts_receivable,
            "shareholder_equity": shareholder_equity,
            "research_and_development_expense": research_and_development_expense,
            "research_and_development_investment": research_and_development_investment,
            "foreign_revenue": foreign_revenue,
            "days_sales_outstanding": days_sales_outstanding,
            "debt_to_equity_ratio": debt_to_equity_ratio,
            "foreign_revenue_percent": foreign_revenue_percent,
            "revenue_streams_summary": revenue_streams_summary, # Q1 - Verbal Question
            "customer_base": customer_base, # Q2 - Verbal Question
            "competitive_landscape": competitive_landscape, # Q3 - Verbal Question
            "growth_strategy": growth_strategy, # Q4 - Verbal Question
            "highlighted_risks": highlighted_risks, # Q5 - Verbal Question
            "regulatory_challenges": regulatory_challenges, # Q6 - Verbal Question
            "net_income_trend_summary": net_income_trend_summary, # Q7 - Verbal Question
            "ebitda_margin": ebitda_margin, # Q8 - Verbal Question
            "operating_expense_commentary": operating_expense_commentary, # Q9 - Verbal Question
            "valuation_commentary": valuation_commentary, # Q10 - Verbal Question
            "capital_expenditures_projects": capex_projects, # Q11 - Verbal Question
            "dividend_and_buyback_policy": dividend_and_buyback_policy, # Q12 - Verbal Question
            "working_capital_efficiency": working_capital_efficiency, # Q13 - Verbal Question
            "management_changes": management_changes, # Q14 - Verbal Question
            "supply_chain_disruptions": supply_chain_disruptions, # Q15 - Verbal Question
            "esg_initiatives": esg_initiatives, # Q16 - Verbal Question
            "esg_controversies": esg_controversies, # Q17 - Verbal Question
            "governance_structure": governance_structure, # Q18 - Verbal Question
            "debt_sustainability_commentary": debt_sustainability_commentary, # Q19 - Verbal Question
            "debt_refinancing_activity": debt_refinancing_activity, # Q20 - Verbal Question
            "technology_impact_on_operations": technology_impact_on_operations, # Q21 - Verbal Question
            "emerging_tech_investments": emerging_tech_investments, # Q22 - Verbal Question
            "intellectual_property_assets": intellectual_property_assets, # Q23 - Verbal Question
            "research_and_development_commentary": research_and_development_commentary, # Q24 - Verbal Question
            "brand_positioning": brand_positioning, # Q25 - Verbal Question
            "rebranding_or_marketing_shift": rebranding_or_marketing_shift, # Q26 - Verbal Question
            "macroeconomic_sensitivity": macroeconomic_sensitivity, # Q27 - Verbal Question
            "geopolitical_and_economic_impacts": geopolitical_and_economic_impacts, # Q28 - Verbal Question
            "growth_scenarios": growth_scenarios, # Q29 - Verbal Question
            "forward_looking_statement": forward_looking_statement, # Q30 - Verbal Question
        })

        # Save progress after each document
        df_so_far = pd.DataFrame(rows)
        df_so_far.to_csv(output_file_path, index=False)
        print(f"[Checkpoint] Saved progress after: {folder_name}")

    return pd.DataFrame(rows)


# ----------------------------
# Main Execution Block
# ----------------------------
if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)

    query_results_dir = os.path.join(project_root, "output", "query_results_v2")
    query_results_dir = get_short_path(query_results_dir)

    # Load company tickers JSON
    tickers_path = os.path.join(project_root, "output", "company_tickers.json")
    with open(tickers_path, "r", encoding="utf-8") as f:
        company_tickers = json.load(f)

    df = extract_metadata_table(query_results_dir, company_tickers)

    print(df.head())
    output_path_new = os.path.join(project_root, "output_new", "final_metadata_table_new.csv")
    df.to_csv(output_path_new, index=False)
    print(f"[saved] Metadata table saved to: {output_path_new}")

    output_path = os.path.join(project_root, "output", "final_metadata_table.csv")
    df.to_csv(output_path, index=False)
    print(f"[Saved] Metadata table saved to: {output_path}")
