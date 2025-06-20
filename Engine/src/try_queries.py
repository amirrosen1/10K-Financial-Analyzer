import os
import json
import pandas as pd
import numpy as np
from extracting_insights import *

# Define the company and year manually
company = "MICROSOFT CORP"
year = 2024

INSIGHT_FUNCTIONS = {
    1: (get_operating_income, 3),
    2: (get_gross_profit, 3),
    3: (get_eps, 3),
    4: (get_cash_flow_operating_activities, 3),
    5: (get_capital_expenditures, 3),
    6: (get_total_liabilities, 3),
    7: (get_total_assets, 3),
    8: (get_stock_activity, 3),
    9: (get_marketing_sales_expense, 3),
    10: (get_fiscal_year_end, 2),
    11: (highest_net_sales_by_year, 2),
    12: (average_tech_net_sales_by_year, 2),
    13: (get_net_income_trend, 2),
    14: (get_yoy_revenue_growth, 2),
    15: (company_largest_net_income_drop, 1),
    16: (highest_average_revenue_last_3_years, 1),
    17: (companies_consistently_above_average, 1),
    18: (company_vs_industry_growth, 2),
    19: (get_companies_by_marketing_revenue_correlation, 1),
    20: (get_outperforming_companies_in_growth_and_margin, 1),
    21: (get_asset_turnover_trend, 2),
    22: (companies_higher_than, 3),
    23: (consistently_increasing_net_sales, 1),
    24: (most_volatile_net_sales_company, 1),
    25: (forecast_net_income, 2),
    26: (predict_decline_next_year, 1),
    27: (predict_revenue_surpass_year, 4),
    28: (predict_next_year_capex, 2),
    29: (predict_years_to_double_revenue, 2),
    30: (predict_liabilities_exceed_assets, 2),
    31: (get_revenue_streams_summary, 3),
    32: (get_customer_base_summary, 3),
    33: (get_competitive_landscape, 3),
    34: (get_growth_strategy, 3),
    35: (get_highlighted_risks, 3),
    36: (get_regulatory_challenges, 3),
    37: (get_net_income_trend_summary, 3),
    38: (get_ebitda_margin_comparison, 3),
    39: (get_operating_expense_commentary, 3),
    40: (get_valuation_commentary, 3),
    41: (get_capital_expenditure_projects, 3),
    42: (get_dividend_and_buyback_policy, 3),
    43: (analyze_working_capital_efficiency, 3),
    44: (analyze_management_changes, 3),
    45: (analyze_supply_chain_disruptions, 3),
    46: (analyze_esg_initiatives, 3),
    47: (analyze_esg_controversies, 3),
    48: (analyze_governance_structure, 3),
    49: (analyze_debt_sustainability, 3),
    50: (analyze_debt_refinancing, 3),
    51: (analyze_technology_impact, 3),
    52: (analyze_emerging_tech_investments, 3),
    53: (analyze_intellectual_property, 3),
    54: (analyze_r_and_d_investment, 3),
    55: (analyze_brand_positioning, 3),
    56: (analyze_rebranding_or_marketing_shift, 3),
    57: (analyze_macroeconomic_sensitivity, 3),
    58: (analyze_geopolitical_and_economic_impacts, 3),
    59: (analyze_growth_scenarios, 3),
    60: (analyze_forward_looking_statements, 3),
}


QUESTIONS = [
    "What was the company’s operating income?",
    "What was the gross profit?",
    "What was the earnings per share (EPS)?",
    "What was the cash flow from operating activities?",
    "What were the capital expenditures?",
    "What was the total liabilities?",
    "What were the total assets?",
    "Did the company issue or repurchase stock?",
    "How much did the company spend on marketing or sales?",
    "What is the fiscal year-end date for the company?",
    "Which company had the highest total net sales in a given year?",
    "What is the average total net sales of technology sector companies in a given year?",
    "How has the company's net income changed over the last 5 years?",
    "What is the year-over-year growth rate in revenue?",
    "Which company had the largest drop in net income between any two consecutive years?",
    "Which company had the highest average revenue over the past 3 years?",
    "Which companies consistently outperformed the average revenue across all companies for the same year?",
    "Is the company’s revenue growth rate above or below the industry average over the past 3 years?",
    "Which companies show the strongest correlation between marketing expenses and revenue over time?",
    "Based on 3-year trends, what companies are outperforming peers in terms of both growth and margin improvement?",
    "How has the company's efficiency changed over time in converting assets into revenue (Asset Turnover Ratio)?",
    "Which companies had higher total net sales than a given company in a given year?",
    "Which companies had a consistent increase in total net sales over 3 consecutive years?",
    "Which company had the most volatile total net sales over time?",
    "What will be the company’s projected net income for next year(s)?",
    "Predict which companies are likely to report a decline in net income next year.",
    "When is the company likely to surpass $X in annual revenue?",
    "Can we predict a company’s future capital expenditures based on revenue growth and past investment behavior?",
    "How long will it take for a company to double its revenue?",
    "When will a company's liabilities exceed its assets (if ever)?",
    "What are the primary revenue streams for the company, and how have they evolved over the past three years?",
    "How diversified is the company's customer base according to the latest 10-K?",
    "Identify the main competitors mentioned in the 10-K and explain the competitive landscape.",
    "How does the company describe its growth strategy and future objectives?",
    "What major risks or uncertainties did the company highlight?",
    "Does the company face any notable regulatory challenges?",
    "What is the trend of the company's net income over the last three fiscal years?",
    "How does the company's EBITDA margin compare with the industry average?",
    "Describe any unusual or significant changes in operating expenses highlighted in the 10-K.",
    "Based on current financials and market conditions, what insights can be derived about the company's valuation?",
    "What major capital expenditures did the company undertake, and what could be their long-term impacts?",
    "Can you identify and discuss the company’s current dividend policy or share repurchase strategies?",
    "How effective has the company been at managing inventory and accounts receivable compared to peers?",
    "Are there any management changes or board restructuring plans mentioned, and what could be their impact?",
    "Did the company experience disruptions in its supply chain, and how does this compare to the broader industry situation?",
    "What ESG initiatives or sustainability practices has the company emphasized in the 10-K?",
    "Has the company faced any ESG-related controversies or litigations recently?",
    "Describe how the company's governance structure aligns with best practices within its industry.",
    "What is the company's current debt-to-equity ratio, and how sustainable is its debt level?",
    "Has the company recently refinanced or restructured its debt, and if so, what are the implications?",
    "How have recent technological advancements in the industry affected the company's operations?",
    "Does the company explicitly mention emerging industry trends or technologies they're investing in?",
    "What significant patents or intellectual property assets?",
    "Describe the company's investment in R&D compared to industry benchmarks.",
    "How does the company position its brand in the marketplace, based on information from the 10-K and broader market knowledge?",
    "Did the company undergo any rebranding or significant marketing shifts?",
    "How sensitive is the company to macroeconomic conditions, such as inflation, interest rate changes, or currency fluctuations?",
    "Has the company described any direct impacts from global geopolitical events or economic shifts?",
    "Based on current financials and market conditions, what are plausible growth scenarios for the company over the next three years?",
    "What forward-looking statements or future commitments did the company emphasize, and how realistic are these in the context of current market conditions?"
]


def result_to_string(value, q_id=None):
    if isinstance(value, dict):
        if q_id == 14:
            return f"Revenue grew {value['growth_rate (%)']}% from {value['from_year']} to {value['to_year']}."
        elif q_id == 15:
            return f"{value['company']} had the largest net income drop of ${float(value['drop_amount']):,.0f} from {value['from_year']} to {value['to_year']}."
        elif q_id == 16:
            return f"{value['company']} had the highest average revenue of ${float(value['average_revenue']):,.0f} over the last 3 years."
        elif q_id == 18:
            return value['comparison']
        elif q_id == 26 and isinstance(value, dict):
            lines = []
            for company, data in value.items():
                try:
                    last = float(data["last_net_income"])
                    next_val = float(data["predicted_next_year"])
                    last_year = data["last_year"]
                    if data["decline_expected"]:
                        lines.append(
                            f"{company} is expected to report a decline in net income in {last_year + 1} (from ${last:,.0f} to ${next_val:,.0f}).")
                    else:
                        lines.append(
                            f"{company} is expected to grow its net income in {last_year + 1} (from ${last:,.0f} to ${next_val:,.0f}).")
                except Exception as e:
                    lines.append(f"Error processing {company}: {e}")
            return "\n".join(lines)
        elif q_id == 27:
            target_revenue = float(str(value['target_revenue']).replace("$", "").replace(",", ""))
            return f"{value['company']} is expected to surpass ${target_revenue:,.0f} in revenue in {value['predicted_year']}."
        elif q_id == 28:
            return f"The predicted capital expenditures for next year are ${float(value['predicted_next_year_capex']):,.0f}."
        elif q_id == 29:
            return f"{value['company']} is expected to double its revenue in {value['years_to_double']} year(s), reaching ${float(value['target_revenue']):,.0f}."
        elif q_id == 30:
            return f"{value['company']}'s liabilities may exceed assets in {value['predicted_crossover_year']} with liabilities of ${float(value['predicted_liabilities']):,.0f}."
        return "; ".join([f"{k}: {v}" for k, v in value.items()])

    elif isinstance(value, list):
        if all(isinstance(x, dict) for x in value):
            return "; ".join([", ".join(f"{k}: {v}" for k, v in item.items()) for item in value])
        return "; ".join(str(x) for x in value)
    return str(value)

def run_all_insights():
    df = pd.read_csv("output/final_metadata_table.csv")
    match = df[(df["company_name"] == company) & (df["year"] == year)]

    if match.empty:
        print(f"[❌] No match found for company='{company}', year={year}")
        return

    folder_name = match.iloc[0]["folder_name"]
    output_dir = "output/json_answers"
    os.makedirs(output_dir, exist_ok=True)

    print("==============================")
    print("Running Insight Queries...")
    print("==============================\n")
    print(f"\n---- COMPANY: {company} | YEAR: {year} ----")

    results = {}

    for i in range(1, 61):
        fn_entry = INSIGHT_FUNCTIONS.get(i)
        if not fn_entry:
            continue

        fn, nargs = fn_entry
        try:
            if i == 27:
                result = fn(company=company, target_revenue=1e11, df=df)
            elif nargs == 4:
                result = fn(company, year, df, None)
            elif nargs == 3:
                result = fn(company, year, df)
            elif nargs == 2:
                if i in [10, 13, 14, 18, 21, 25, 28, 29, 30]:
                    result = fn(company, df)
                else:
                    result = fn(year, df)
            elif nargs == 1:
                result = fn(df)
            else:
                result = f"Unsupported function signature for Q{i:02d}"
        except Exception as e:
            result = f"Q{i:02d} ERROR: {e}"

        question = QUESTIONS[i - 1]
        results[question] = result_to_string(result, q_id=i)
        print(f"\nQ{i:02d}: {results[question]}\n")

    output_path = os.path.join(output_dir, f"{folder_name}.json")

    def convert_numpy(obj):
        if isinstance(obj, (np.integer, np.int64)):
            return int(obj)
        elif isinstance(obj, (np.floating, np.float64)):
            return float(obj)
        elif isinstance(obj, (np.bool_)):
            return bool(obj)
        elif isinstance(obj, (np.ndarray,)):
            return obj.tolist()
        return str(obj)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump({
            "folder_name": folder_name,
            "company": company,
            "year": year,
            "results": results
        }, f, indent=2, ensure_ascii=False, default=convert_numpy)
    print(f"[✅ Saved] {output_path}")

if __name__ == "__main__":
    run_all_insights()

