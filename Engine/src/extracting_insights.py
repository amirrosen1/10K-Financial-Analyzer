import os
os.environ['MPLCONFIGDIR'] = '/tmp/matplotlib'

import matplotlib.pyplot as plt
import pandas as pd
import torch
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from sklearn.linear_model import LinearRegression
import numpy as np
from scipy.stats import pearsonr
import statistics
import re
from statsmodels.tsa.arima.model import ARIMA
import warnings


# =========================
# Group A – Direct Lookups
# =========================

# 1. What was the company’s operating income in [year]?
# Strategy: Look for the entry that matches the given company and year, then return the "operating_income" field.
def get_operating_income(company, year, df):
    """
    Returns the operating income of a given company for a specific year.
    Handles missing or null data safely.

    Parameters:
        company (str): Company name to match
        year (int): Year of the report
        df (pd.DataFrame): The DataFrame containing the metadata

    Returns:
        float or str: Operating income if found, or a message if not available
    """
    row = df[(df["company_name"] == company) & (df["year"] == year)]

    if row.empty:
        return f"No data found for {company} in {year}."

    value = row["operating_income"].values[0]

    if pd.isna(value):
        return f"Operating income data is missing for {company} in {year}."

    return value


# 2. What was the company’s gross profit in [year]?
# Strategy: Return the "gross_profit" field directly if present.
def get_gross_profit(company, year, df):
    """
    Returns the gross profit of a given company for a specific year.
    Handles missing or null data safely.

    Parameters:
        company (str): Company name to match
        year (int): Year of the report
        df (pd.DataFrame): The DataFrame containing the metadata

    Returns:
        float or str: Gross profit if found, or a message if not available
    """
    row = df[(df["company_name"] == company) & (df["year"] == year)]

    if row.empty:
        return f"No data found for {company} in {year}."

    value = row["gross_profit"].values[0]

    if pd.isna(value):
        return f"Gross profit data is missing for {company} in {year}."

    return value


# 3. What was the company's earnings per share (EPS) in [year]?
# Strategy: Return the "eps" field from the corresponding entry.
def get_eps(company, year, df):
    """
    Returns the earnings per share (EPS) of a given company for a specific year.
    Handles missing or null data safely.

    Parameters:
        company (str): Company name to match
        year (int): Year of the report
        df (pd.DataFrame): The DataFrame containing the metadata

    Returns:
        float or str: EPS value if found, or a message if not available
    """
    row = df[(df["company_name"] == company) & (df["year"] == year)]

    if row.empty:
        return f"No data found for {company} in {year}."

    value = row["earnings_per_share"].values[0]

    if pd.isna(value):
        return f"EPS data is missing for {company} in {year}."

    return value


# 4. What was the company’s cash flow from operating activities in [year]?
# Strategy: Return the value under "cash_flow_operating_activities".
def get_cash_flow_operating_activities(company, year, df):
    """
    Returns the cash flow from operating activities for a given company and year.
    Handles missing or null data safely.

    Parameters:
        company (str): Company name to match
        year (int): Year of the report
        df (pd.DataFrame): The DataFrame containing the metadata

    Returns:
        float or str: Cash flow value if found, or a message if not available
    """
    row = df[(df["company_name"] == company) & (df["year"] == year)]

    if row.empty:
        return f"No data found for {company} in {year}."

    value = row["cash_flow_operating_activities"].values[0]

    if pd.isna(value):
        return f"Cash flow from operating activities is missing for {company} in {year}."

    return value



# 5. What were the company’s capital expenditures in [year]?
# Strategy: Return the value under "capital_expenditures".
def get_capital_expenditures(company, year, df):
    """
    Returns the capital expenditures for a given company and year.
    Handles missing or null data safely.

    Parameters:
        company (str): Company name to match
        year (int): Year of the report
        df (pd.DataFrame): The DataFrame containing the metadata

    Returns:
        float or str: Capital expenditures value if found, or a message if not available
    """
    row = df[(df["company_name"] == company) & (df["year"] == year)]

    if row.empty:
        return f"No data found for {company} in {year}."

    value = row["capital_expenditures"].values[0]

    if pd.isna(value):
        return f"Capital expenditures data is missing for {company} in {year}."

    return value



# 6. What was the company's total liabilities in [year]?
# Strategy:
# - Find the record matching the given company and year.
# - Return the value under "total_liabilities" if it exists.
def get_total_liabilities(company, year, df):
    """
    Returns the total liabilities for a given company and year.
    Handles missing or null data safely.

    Parameters:
        company (str): Company name to match
        year (int): Year of the report
        df (pd.DataFrame): The DataFrame containing the metadata

    Returns:
        float or str: Total liabilities value if found, or a message if not available
    """
    row = df[(df["company_name"] == company) & (df["year"] == year)]

    if row.empty:
        return f"No data found for {company} in {year}."

    value = row["total_liabilities"].values[0]

    if pd.isna(value):
        return f"Total liabilities data is missing for {company} in {year}."

    return value



# 7. What were the company's total assets in [year]?
# Strategy:
# - Find the record matching the given company and year.
# - Return the value under "total_assets" if it exists.
def get_total_assets(company, year, df):
    """
    Returns the total assets for a given company and year.
    Handles missing or null data safely.

    Parameters:
        company (str): Company name to match
        year (int): Year of the report
        df (pd.DataFrame): The DataFrame containing the metadata

    Returns:
        float or str: Total assets value if found, or a message if not available
    """
    row = df[(df["company_name"] == company) & (df["year"] == year)]

    if row.empty:
        return f"No data found for {company} in {year}."

    value = row["total_assets"].values[0]

    if pd.isna(value):
        return f"Total assets data is missing for {company} in {year}."

    return value



# 8. Did the company issue or repurchase stock in [year]?
# Strategy:
# - Find the record matching the given company and year.
# - Check fields like "stock_issuance" or "stock_repurchases".
# - If either exists and is non-zero, return a full friendly sentence with the amount.
# - If no activity, return a friendly sentence stating no stock activity occurred.

def get_stock_activity(company, year, df):
    """
    Describes stock issuance or repurchase activity for a given company and year.
    Handles missing or null data safely.

    Parameters:
        company (str): Company name to match
        year (int): Year of the report
        df (pd.DataFrame): The DataFrame containing the metadata

    Returns:
        str: A friendly message summarizing the company's stock activity
    """
    row = df[(df["company_name"] == company) & (df["year"] == year)]

    if row.empty:
        return f"No data available for {company} in {year}."

    issued = row["stock_issuance"].values[0]
    repurchased = row["stock_repurchases"].values[0]

    if not pd.isna(issued) and issued != 0:
        return f"In {year}, {company} issued stock worth ${issued:,.0f}."
    elif not pd.isna(repurchased) and repurchased != 0:
        return f"In {year}, {company} repurchased stock worth ${repurchased:,.0f}."
    else:
        return f"In {year}, {company} did not issue or repurchase any stock."



# 9. How much did the company spend on marketing or sales in [year]?
# Strategy:
# - Find the record matching the given company and year.
# - Prefer using the "sales_and_marketing_expense" field if available.
# - If not available, fallback to "sga_expense" (Selling, General, Administrative Expenses).
# - If both are missing, return a friendly message.
# - Format the output nicely for readability.

def get_marketing_sales_expense(company, year, df):
    """
    Returns how much a company spent on marketing or sales in a specific year.
    Prefers the marketing-specific field, falls back to SG&A if missing.

    Parameters:
        company (str): Company name to match
        year (int): Year of the report
        df (pd.DataFrame): The DataFrame containing the metadata

    Returns:
        str: A formatted message describing the marketing/sales or SG&A expense
    """
    row = df[(df["company_name"] == company) & (df["year"] == year)]

    if row.empty:
        return f"No data available for {company} in {year}."

    marketing_expense = row["sales_and_marketing_expense"].values[0]
    sga_expense = row["sg_a_expense"].values[0]

    if not pd.isna(marketing_expense):
        return f"In {year}, {company} spent ${marketing_expense:,.0f} on marketing and sales."
    elif not pd.isna(sga_expense):
        return (f"In {year}, {company} did not report marketing expenses separately, "
                f"but reported ${sga_expense:,.0f} under SG&A (Selling, General, and Administrative Expenses).")
    else:
        return f"Marketing and sales expense data not available for {company} in {year}."



# 10. What is the fiscal year-end date for the company?
# Strategy:
# - Search for any record matching the given company.
# - Retrieve the "fiscal_year_end" field.
# - If available, return a friendly message with the date.
# - If missing, return a message indicating that the information is unavailable.

def get_fiscal_year_end(company, df):
    """
    Returns the fiscal year-end date for a given company.
    Searches across all years and returns the first non-null date found.

    Parameters:
        company (str): Company name to match
        df (pd.DataFrame): The DataFrame containing the metadata

    Returns:
        str: A message indicating the fiscal year-end date or a fallback if missing
    """
    rows = df[df["company_name"] == company]

    if rows.empty:
        return f"No data available for {company}."

    for _, row in rows.iterrows():
        fiscal_year_end = row["fiscal_year_end"]
        if pd.notna(fiscal_year_end):
            return f"The fiscal year-end date for {company} is {fiscal_year_end}."

    return f"Fiscal year-end date not available for {company}."



# 11. Which company had the highest total net sales in a given year?
# Strategy:
# - User provides the year of interest.
# - Filter entries for that year, then return the company with the maximum total_net_sales.

def highest_net_sales_by_year(year, df):
    """
    Returns the company with the highest total net sales in a given year.

    Parameters:
        year (int): The year to search within
        df (pd.DataFrame): The DataFrame containing the metadata

    Returns:
        dict or str: The top company with its sales, or a message if no data is available
    """
    filtered = df[(df["year"] == year) & (df["total_revenue"].notna())]

    if filtered.empty:
        return f"No data available for the year {year}."

    top_row = filtered.loc[filtered["total_revenue"].idxmax()]
    return {
        "year": year,
        "company": top_row["company_name"],
        "total_net_sales": top_row["total_revenue"]
    }



# 12. What is the average total net sales of technology sector companies in a given year?
# Strategy:
# - User provides the year of interest.
# - Filter entries to those in the "Technology" sector.
# - Collect total_net_sales values for that year.
# - Compute and return the average.

def average_tech_net_sales_by_year(year, df):
    """
    Returns the average total net sales of companies in the technology sector for a specific year.
    Matches sector descriptions using regex for words like 'tech' or 'technology'.

    Parameters:
        year (int): The year to filter by
        df (pd.DataFrame): The DataFrame containing the metadata

    Returns:
        dict or str: Average net sales for the Technology sector, or a message if no data is found
    """
    # Define a regex pattern to match tech-related sector descriptions
    tech_pattern = re.compile(r"\btech(nology)?\b", re.IGNORECASE)

    filtered = df[
        (df["year"] == year) &
        (df["sector"].notna()) &
        (df["sector"].apply(lambda x: bool(tech_pattern.search(str(x))))) &
        (df["total_revenue"].notna())
    ]

    if filtered.empty:
        return f"No technology sector revenue data available for the year {year}."

    avg_sales = round(filtered["total_revenue"].mean(), 2)

    return {
        "sector": "Technology",
        "year": year,
        "average_net_sales": avg_sales
    }





# =========================
# Group B – Trend & Math-Based
# =========================

# 1. How has [Company]'s net income changed over the last 5 years?
# Strategy: Filter all records for the company, sort by year, extract net income,
# then compute and return year-over-year (YoY) changes as a list of {year, net_income, change_from_previous}.
def get_net_income_trend(company, df, recent_years=2):
    """
    Calculates year-over-year net income changes for a company over the last N years.

    Parameters:
        company (str): Company name to match
        df (pd.DataFrame): The DataFrame containing the metadata
        recent_years (int): Number of most recent years to include

    Returns:
        list or str: A list of dictionaries showing the trend, or a message if not enough data is available
    """
    company_data = df[
        (df["company_name"] == company) &
        (df["net_income"].notna())
    ].sort_values("year")

    if company_data.shape[0] < 2:
        return "Not enough data for trend analysis."

    # Take only the last `recent_years` rows
    company_data = company_data.tail(recent_years)

    trend = []
    prev_net_income = None

    for _, row in company_data.iterrows():
        year = row["year"]
        net_income = row["net_income"]

        if prev_net_income is not None and prev_net_income != 0:
            change = (net_income - prev_net_income) / prev_net_income * 100
        else:
            change = None

        trend.append({
            "year": year,
            "net_income": net_income,
            "change_from_previous_year (%)": round(change, 2) if change is not None else None
        })

        prev_net_income = net_income

    return trend


# 2. What is the year-over-year growth rate in revenue for [Company]?
# Strategy: Get revenue for two most recent consecutive years, compute growth rate.
def get_yoy_revenue_growth(company, df):
    """
    Calculates the year-over-year growth rate in total revenue for the given company.
    Uses the two most recent years with available data.

    Parameters:
        company (str): Company name to match
        df (pd.DataFrame): The DataFrame containing the metadata

    Returns:
        dict or str: Growth rate info or error message
    """
    company_data = df[
        (df["company_name"] == company) &
        (df["total_revenue"].notna())
    ].sort_values("year")

    if company_data.shape[0] < 2:
        return "Not enough data for YoY growth calculation."

    # Get the last two years
    latest_row = company_data.iloc[-1]
    prev_row = company_data.iloc[-2]

    rev_latest = latest_row["total_revenue"]
    rev_prev = prev_row["total_revenue"]

    if rev_prev == 0:
        return "Previous year revenue is zero, cannot compute growth rate."

    growth_rate = (rev_latest - rev_prev) / rev_prev * 100

    return {
        "from_year": int(prev_row["year"]),
        "to_year": int(latest_row["year"]),
        "growth_rate (%)": round(growth_rate, 2)
    }



# 3. Which company had the largest drop in net income between any two consecutive years?
# Strategy: For each company, compute YoY differences in net income.
# Track the largest negative difference and return that company and the years involved.
def company_largest_net_income_drop(df):
    """
    Finds the company with the largest drop in net income between any two consecutive years.

    Parameters:
        df (pd.DataFrame): The DataFrame containing the metadata

    Returns:
        dict or str: Info about the largest drop or a fallback message
    """
    max_drop = None
    result = None

    # Drop rows with missing company name or net_income
    valid_df = df[df["net_income"].notna() & df["company_name"].notna()]

    for company in valid_df["company_name"].unique():
        company_records = valid_df[valid_df["company_name"] == company].sort_values("year")

        if company_records.shape[0] < 2:
            continue

        previous_income = None
        previous_year = None

        for _, row in company_records.iterrows():
            year = row["year"]
            income = row["net_income"]

            if previous_income is not None:
                drop = income - previous_income
                if max_drop is None or drop < max_drop:
                    max_drop = drop
                    result = {
                        "company": company,
                        "from_year": previous_year,
                        "to_year": year,
                        "drop_amount": round(drop, 2)
                    }

            previous_income = income
            previous_year = year

    return result if result else "No valid net income drops found."



# 4. Which company had the highest average revenue over the past 3 years?
# Strategy:
# - For each company:
#   - Sort their revenue (total_net_sales) by year.
#   - Take the last 3 years (or fewer if missing).
#   - Calculate the average revenue.
# - Return the company with the highest 3-year average.
def highest_average_revenue_last_3_years(df):
    """
    Determines which company had the highest average total revenue over the most recent 3 years.

    Parameters:
        df (pd.DataFrame): The DataFrame containing the metadata

    Returns:
        dict or str: Company name and average revenue, or a message if data is insufficient
    """
    highest_avg = None
    best_company = None

    # Filter valid rows
    valid_df = df[df["total_revenue"].notna() & df["company_name"].notna()]

    for company in valid_df["company_name"].unique():
        company_data = valid_df[valid_df["company_name"] == company].sort_values("year", ascending=False)

        recent_revenues = company_data["total_revenue"].head(3).tolist()

        if len(recent_revenues) == 0:
            continue

        avg_revenue = sum(recent_revenues) / len(recent_revenues)

        if highest_avg is None or avg_revenue > highest_avg:
            highest_avg = avg_revenue
            best_company = company

    return {
        "company": best_company,
        "average_revenue": round(highest_avg, 2)
    } if best_company else "No sufficient data."


# 5. Which companies consistently outperformed the average revenue across all companies for the same year?
# Strategy:
# - For each year:
#   - Calculate the average total_net_sales across all companies.
# - For each company:
#   - Check if they beat the yearly average every year they appear.
# - Return companies that consistently outperformed.
def companies_consistently_above_average(df):
    """
    Identifies companies that consistently outperformed the average total revenue
    across all companies for each year in which they reported.

    Parameters:
        df (pd.DataFrame): The DataFrame containing the metadata

    Returns:
        list or str: List of outperforming companies or a message if none found
    """
    # Filter valid rows
    valid_df = df[df["total_revenue"].notna() & df["company_name"].notna()]

    # Step 1: Compute average total_revenue per year
    year_avg = valid_df.groupby("year")["total_revenue"].mean().to_dict()

    # Step 2: Group by company
    outperformers = []

    for company in valid_df["company_name"].unique():
        company_data = valid_df[valid_df["company_name"] == company]

        consistently_above = True
        for _, row in company_data.iterrows():
            year = row["year"]
            revenue = row["total_revenue"]
            if revenue < year_avg.get(year, float("inf")):
                consistently_above = False
                break

        if consistently_above:
            outperformers.append(company)

    return outperformers if outperformers else "No companies consistently outperformed."


# 6. Is [Company]’s revenue growth rate above or below the industry average over the past 3 years?
# Strategy:
# - Compute the company's YoY growth over its last 3 years.
# - Compute the industry-wide YoY growth (average of all companies over same years).
# - Compare them.
def company_vs_industry_growth(company, df):
    """
    Compares the average revenue growth rate of a company to the industry average over the past 3 years.

    Parameters:
        company (str): Company name to match
        df (pd.DataFrame): The DataFrame containing the metadata

    Returns:
        dict or str: Comparison result or a message if not enough data
    """

    def calculate_yoy_growth(pairs):
        """
        Helper to calculate year-over-year growth from a list of (year, revenue) tuples.
        """
        pairs = sorted(pairs, key=lambda x: x[0])
        growth_rates = []
        for i in range(1, len(pairs)):
            prev_rev = pairs[i-1][1]
            curr_rev = pairs[i][1]
            if prev_rev == 0 or pd.isna(prev_rev) or pd.isna(curr_rev):
                continue
            growth = (curr_rev - prev_rev) / prev_rev * 100
            growth_rates.append(growth)
        return growth_rates

    # Step 1: Company's YoY growth
    company_df = df[(df["company_name"] == company) & (df["total_revenue"].notna())]
    if company_df.shape[0] < 2:
        return f"Not enough data to compute {company}'s growth."

    company_revenue_by_year = list(zip(company_df["year"], company_df["total_revenue"]))
    company_growth = calculate_yoy_growth(company_revenue_by_year)[-3:]
    if not company_growth:
        return f"Not enough valid YoY growth data for {company}."

    avg_company_growth = sum(company_growth) / len(company_growth)

    # Step 2: Industry-wide YoY growth
    industry_df = df[df["total_revenue"].notna()]
    industry_avg_by_year = industry_df.groupby("year")["total_revenue"].mean().sort_index()
    industry_growth = calculate_yoy_growth(list(industry_avg_by_year.items()))[-3:]

    if not industry_growth:
        return "Not enough industry data to compute growth."

    avg_industry_growth = sum(industry_growth) / len(industry_growth)

    comparison = "above" if avg_company_growth > avg_industry_growth else "below"

    return {
        "company_avg_growth (%)": round(avg_company_growth, 2),
        "industry_avg_growth (%)": round(avg_industry_growth, 2),
        "comparison": f"{company}'s growth is {comparison} the industry average."
    }


# 7. Which companies show the strongest correlation between marketing expenses and revenue over time?
# Strategy:
# - For each company:
#   - Extract years with both "sales_and_marketing_expense" (or "sga_expense") and "total_net_sales".
#   - Keep only valid data points (no missing values).
#   - Require at least 3 years of data.
# - Calculate Pearson correlation coefficient between marketing spend and revenue.
# - Rank companies by correlation strength.
# - Return top companies with strongest positive correlation.

def get_companies_by_marketing_revenue_correlation(df, min_years=3):
    """
    Calculates the Pearson correlation between marketing expenses and total revenue
    for each company and returns the companies ranked by correlation strength.

    Parameters:
        df (pd.DataFrame): The DataFrame containing the metadata
        min_years (int): Minimum number of data points required to compute correlation

    Returns:
        list or str: List of companies with correlation coefficients, or a message if insufficient data
    """
    correlations = []

    # Filter only companies with valid name
    for company in df["company_name"].dropna().unique():
        company_df = df[df["company_name"] == company].copy()

        # Use marketing expense or fallback to SG&A
        company_df["marketing_expense"] = company_df["sales_and_marketing_expense"]
        fallback_mask = company_df["marketing_expense"].isna()
        company_df.loc[fallback_mask, "marketing_expense"] = company_df.loc[fallback_mask, "sg_a_expense"]

        valid = company_df[company_df["total_revenue"].notna() & company_df["marketing_expense"].notna()]

        if valid.shape[0] >= min_years:
            try:
                corr, _ = pearsonr(valid["marketing_expense"], valid["total_revenue"])
                correlations.append({
                    "company": company,
                    "correlation_coefficient": round(corr, 3)
                })
            except Exception:
                continue

    correlations = sorted(correlations, key=lambda x: x["correlation_coefficient"], reverse=True)

    return correlations if correlations else "No companies have sufficient data to compute correlations."


# 8. Based on 3-year trends, what companies are outperforming peers in terms of both growth and margin improvement?
# Strategy:
# - For each company:
#   - Extract last 3 years of total_net_sales and net_income.
#   - Compute 3-year CAGR of revenue.
#   - Compute change in profit margin (last margin - first margin).
# - Flag companies with positive revenue CAGR and positive margin improvement.
# - Return a list of outperformers with their Growth % and Margin Delta %.

def get_outperforming_companies_in_growth_and_margin(df, min_years=3):
    """
    Identifies companies that are outperforming peers in both revenue growth (CAGR) and profit margin improvement
    over the past N years.

    Parameters:
        df (pd.DataFrame): The DataFrame containing the metadata
        min_years (int): Minimum number of years of data required (default is 3)

    Returns:
        list or str: List of outperforming companies or a message if none found
    """
    outperformers = []

    valid_df = df[df["company_name"].notna() & df["total_revenue"].notna() & df["net_income"].notna()]

    for company in valid_df["company_name"].unique():
        company_df = valid_df[valid_df["company_name"] == company].sort_values("year")

        if company_df.shape[0] < min_years:
            continue

        recent = company_df.tail(min_years)

        start_year, end_year = recent["year"].iloc[0], recent["year"].iloc[-1]
        start_rev, end_rev = recent["total_revenue"].iloc[0], recent["total_revenue"].iloc[-1]

        if start_rev == 0 or start_year == end_year:
            continue

        # CAGR Calculation
        years_span = end_year - start_year
        cagr = (end_rev / start_rev) ** (1 / years_span) - 1

        # Margin change: (Net Income / Revenue)
        start_margin = recent["net_income"].iloc[0] / start_rev if start_rev else 0
        end_margin = recent["net_income"].iloc[-1] / end_rev if end_rev else 0
        margin_delta = end_margin - start_margin

        if cagr > 0 and margin_delta > 0:
            outperformers.append({
                "company": company,
                "revenue_cagr (%)": round(cagr * 100, 2),
                "profit_margin_delta (%)": round(margin_delta * 100, 2)
            })

    return outperformers if outperformers else "No outperforming companies found."



# 9. How has [Company]'s efficiency changed over time in converting assets into revenue (Asset Turnover Ratio)?
# Strategy:
# - Extract all years where both total_assets and total_net_sales are available.
# - Compute Asset Turnover = Revenue / Assets for each year.
# - Skip years with missing values or zero assets (to avoid division by zero).
# - Return a list of {year, asset_turnover} entries, sorted by year.

def get_asset_turnover_trend(company, df):
    """
    Computes the Asset Turnover Ratio trend for a given company over the years.
    Asset Turnover = Total Revenue / Total Assets

    Parameters:
        company (str): Name of the company
        df (pd.DataFrame): DataFrame containing the metadata

    Returns:
        list or str: List of {year, asset_turnover} dictionaries or a message if insufficient data
    """
    filtered = df[
        (df["company_name"] == company) &
        df["total_revenue"].notna() &
        df["total_assets"].notna() &
        (df["total_assets"] != 0)
    ]

    if filtered.empty:
        return f"No sufficient data available to compute Asset Turnover for {company}."

    trend = [
        {
            "year": int(row["year"]),
            "asset_turnover": round(row["total_revenue"] / row["total_assets"], 4)
        }
        for _, row in filtered.iterrows()
    ]

    trend = sorted(trend, key=lambda x: x["year"])
    return trend


# 10. Which companies had higher total net sales than a given company in a given year?
# Strategy:
# - User provides the reference company and year.
# - Find that company’s net sales, then compare others from the same year.

def companies_higher_than(company, year, df):
    """
    Finds companies with higher total revenue than a specified company in a given year.

    Parameters:
        company (str): Reference company
        year (int): Year of comparison
        df (pd.DataFrame): DataFrame containing financial data

    Returns:
        dict: Summary including reference company revenue and list of outperformers
    """
    # Filter for the reference company's revenue
    ref_row = df[
        (df["company_name"] == company) &
        (df["year"] == year) &
        df["total_revenue"].notna()
    ]

    if ref_row.empty:
        return f"No revenue data found for {company} in {year}."

    ref_sales = ref_row["total_revenue"].iloc[0]

    # Filter others in the same year with higher revenue
    others = df[
        (df["year"] == year) &
        df["total_revenue"].notna() &
        (df["total_revenue"] > ref_sales)
    ]

    higher_companies = others["company_name"].unique().tolist()

    return {
        "reference_company": company,
        "reference_year": year,
        "reference_sales": round(ref_sales, 2),
        "higher_companies": higher_companies if higher_companies else "No company had higher revenue than the reference."
    }



# 11. Which companies had a consistent increase in total net sales over 3 consecutive years?
# Strategy:
# - For each company:
#   - Sort records by year.
#   - Look for at least one 3-year stretch with increasing sales.

def consistently_increasing_net_sales(df):
    """
    Identifies companies with at least one stretch of 3 consecutive years
    showing increasing total revenue.

    Parameters:
        df (pd.DataFrame): DataFrame containing the metadata

    Returns:
        list or str: List of companies or message if none found
    """
    consistent_companies = []

    valid_df = df[df["total_revenue"].notna() & df["company_name"].notna()]

    for company in valid_df["company_name"].unique():
        company_df = valid_df[valid_df["company_name"] == company].sort_values("year")

        revenues = company_df[["year", "total_revenue"]].dropna().values.tolist()

        for i in range(len(revenues) - 2):
            y1, r1 = revenues[i]
            y2, r2 = revenues[i + 1]
            y3, r3 = revenues[i + 2]

            if r1 < r2 < r3:
                consistent_companies.append(company)
                break  # No need to check further for this company

    return consistent_companies if consistent_companies else "No companies showed consistent growth over 3 years."


# 12. Which company had the most volatile total net sales over time?
# Strategy:
# - For each company:
#   - Compute standard deviation of total_net_sales over all years (min 2).
# - Return the company with the highest volatility.

def most_volatile_net_sales_company(df):
    """
    Identifies the company with the most volatile total revenue across all years,
    measured by standard deviation.

    Parameters:
        df (pd.DataFrame): DataFrame containing financial metadata

    Returns:
        dict or str: Company with the highest volatility or message if not enough data
    """
    volatilities = {}

    grouped = df[df["total_revenue"].notna()].groupby("company_name")

    for company, group in grouped:
        sales = group["total_revenue"].tolist()
        if len(sales) >= 2:
            try:
                volatilities[company] = statistics.stdev(sales)
            except statistics.StatisticsError:
                continue  # In case of constant values or unexpected input

    if not volatilities:
        return "Not enough data to assess volatility for any company."

    most_volatile = max(volatilities, key=volatilities.get)
    return {
        "company": most_volatile,
        "volatility_measure (stdev)": round(volatilities[most_volatile], 2)
    }



# ====================================
# Group C – Forecasting & Prediction
# ====================================

# 1. What will be [Company]’s projected net income for next year(s)?
# Strategy:
# - Extract all known net income values for the company, indexed by year.
# - Apply Holt's Exponential Smoothing to model trend.
# - Forecast net income for N future years (default: next year).

def forecast_net_income(company, df, steps=1):
    """
    Forecasts the net income for a given company using the ARIMA model and displays a plot.

    Parameters:
        company (str): Company name to match
        df (pd.DataFrame): DataFrame containing the financial metadata
        steps (int): Number of years to forecast

    Returns:
        dict or str: Forecasted net income values keyed by year or an error message
    """

    warnings.filterwarnings("ignore")

    # Filter relevant records
    company_df = df[(df["company_name"] == company) & df["net_income"].notna()]
    if len(company_df) < 3:
        return f"Not enough data to forecast net income for {company}"

    # Prepare time series
    series = company_df.set_index("year")["net_income"].sort_index()
    years = series.index.tolist()
    last_year = years[-1]

    try:
        # Fit ARIMA model (you can tune the order as needed)
        model = ARIMA(series, order=(1, 1, 1))
        fit = model.fit()

        # Forecast
        forecast = fit.forecast(steps=steps)
        forecast = forecast.round(2)
        forecast_years = [last_year + i for i in range(1, steps + 1)]
        forecast_dict = dict(zip(forecast_years, forecast))

    except Exception as e:
        return f"Model failed to fit: {e}"

    # Plot
    plt.figure(figsize=(10, 5))
    plt.plot(series.index, series.values, label="Historical Net Income", marker='o')
    plt.plot(forecast_years, forecast.values, label="Forecasted Net Income", marker='x', linestyle='--')
    plt.title(f"Net Income Forecast for {company} (ARIMA)")
    plt.xlabel("Year")
    plt.ylabel("Net Income")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()

    return forecast_dict


# 2. Predict which companies are likely to report a decline in net income next year.
# Strategy:
# - For each company with 3+ years of data, use Holt’s model to forecast next year’s net income.
# - Compare forecasted value to last known net income.
# - If forecast is lower → predict a decline.

def predict_decline_next_year(df):
    """
    Predicts which companies are likely to report a decline in net income next year
    using Holt’s Linear Trend model.

    Parameters:
        df (pd.DataFrame): DataFrame containing financial metadata

    Returns:
        dict: Each company mapped to its last value, forecast, and decline status
    """
    predictions = {}

    # Filter only valid rows
    valid_df = df[df["net_income"].notna() & df["company_name"].notna()]

    for company in valid_df["company_name"].unique():
        company_df = valid_df[valid_df["company_name"] == company].sort_values("year")
        if company_df.shape[0] < 3:
            continue  # Not enough data

        # Build time series
        series = company_df.set_index("year")["net_income"]
        series.index = pd.PeriodIndex(series.index, freq='Y')

        try:
            model = ExponentialSmoothing(series, trend="add", seasonal=None, initialization_method="estimated")
            fit = model.fit()
            forecast = fit.forecast(1)
            forecast_value = forecast.iloc[0]
            last_year = int(str(series.index[-1]))
            last_value = series.iloc[-1]

            predictions[company] = {
                "last_year": last_year,
                "last_net_income": round(last_value, 2),
                "predicted_next_year": round(forecast_value, 2),
                "decline_expected": forecast_value < last_value
            }

        except Exception as e:
            predictions[company] = f"Error in forecasting: {str(e)}"

    return predictions


# 3. When is [Company] likely to surpass $X in annual revenue?
# Strategy:
# - Extract all available total_net_sales values for the company, indexed by year.
# - Filter out any years with missing or None values.
# - Apply Holt’s Linear Trend Exponential Smoothing model to the revenue series.
# - Forecast revenues year-by-year into the future.
# - Find the first year where predicted revenue ≥ target X.
# - If it never crosses, return a message saying so.

def predict_revenue_surpass_year(company, target_revenue, df, max_forecast_years=10):
    """
    Predicts the first year in which a company's total revenue will surpass a target amount,
    using Holt’s Linear Trend Exponential Smoothing.

    Parameters:
        company (str): Company name
        target_revenue (float): Revenue threshold to surpass
        df (pd.DataFrame): DataFrame with financial data
        max_forecast_years (int): How far into the future to forecast (default 10)

    Returns:
        dict or str: Year and revenue prediction or a message if it won't be surpassed
    """
    # Step 1: Extract valid revenue data
    company_df = df[(df["company_name"] == company) & df["total_revenue"].notna()]

    if len(company_df) < 3:
        return f"Not enough data to forecast revenue for {company}."

    # Step 2: Create a time series indexed by year
    series = company_df.set_index("year")["total_revenue"].sort_index()
    series.index = pd.PeriodIndex(series.index, freq='Y')

    # Step 3: Fit Holt’s model and forecast
    try:
        model = ExponentialSmoothing(series, trend="add", seasonal=None, initialization_method="estimated")
        fit = model.fit()

        forecast = fit.forecast(max_forecast_years)
        forecast_years = [int(str(series.index[-1])) + i + 1 for i in range(max_forecast_years)]

        # Step 4: Identify first year exceeding the target
        for year, predicted_value in zip(forecast_years, forecast):
            if predicted_value >= target_revenue:
                return {
                    "company": company,
                    "target_revenue": f"${target_revenue:,.2f}",
                    "predicted_year": year,
                    "predicted_revenue": round(predicted_value, 2)
                }

        return f"{company} is not expected to surpass ${target_revenue:,.2f} within the next {max_forecast_years} years."

    except Exception as e:
        return f"Forecasting error for {company}: {str(e)}"


# 4. Can we predict a company’s future capital expenditures based on revenue growth and past investment behavior?
# Strategy:
# - Extract historical data: total_net_sales (revenue) and capital_expenditures.
# - Compute revenue growth rates (year-over-year % change).
# - Build a dataset where:
#   Features (X) = [current year's revenue, revenue growth %]
#   Target (y) = next year's capital expenditures
# - Train a Linear Regression model.
# - Use the most recent available features to predict next year's CapEx.
# - Handle missing values carefully.

def predict_next_year_capex(company, df):
    """
    Predicts next year's capital expenditures based on revenue and revenue growth
    using a simple Linear Regression model.

    Parameters:
        company (str): The company name
        df (pd.DataFrame): Financial data containing total_revenue and capital_expenditures

    Returns:
        dict or str: Prediction result or error message if not enough data
    """
    # Step 1: Extract relevant records
    company_df = df[
        (df["company_name"] == company) &
        df["total_revenue"].notna() &
        df["capital_expenditures"].notna()
    ][["year", "total_revenue", "capital_expenditures"]].sort_values("year")

    if company_df.shape[0] < 3:
        return f"Not enough data to forecast CapEx for {company}."

    # Step 2: Compute revenue growth (% change year over year)
    company_df["revenue_growth"] = company_df["total_revenue"].pct_change() * 100
    company_df = company_df.dropna()

    if company_df.shape[0] < 2:
        return f"Not enough usable records after cleaning for {company}."

    # Step 3: Construct features and targets
    X = company_df[["total_revenue", "revenue_growth"]].iloc[:-1]
    y = company_df["capital_expenditures"].iloc[1:]

    # Step 4: Train the regression model
    model = LinearRegression()
    model.fit(X, y)

    # Step 5: Use latest year features to predict next year's CapEx
    latest_X = company_df[["total_revenue", "revenue_growth"]].iloc[-1].values.reshape(1, -1)
    predicted_capex = model.predict(latest_X)[0]

    return {
        "company": company,
        "predicted_next_year_capex": round(predicted_capex, 2)
    }


# 5. How long will it take for a company to double its revenue?
# Strategy:
# - Extract total_net_sales history for the company.
# - Drop missing revenue data.
# - Sort by year and get the latest available revenue.
# - Fit Holt’s Linear Trend model to the revenue time series.
# - Forecast future revenues year-by-year.
# - Find when predicted revenue ≥ 2 × current revenue.
# - Return number of years needed, or a message if not achievable.

def predict_years_to_double_revenue(company, df, max_forecast_years=20):
    """
    Predicts how many years it will take for a company to double its current revenue,
    using Holt’s Linear Trend Exponential Smoothing.

    Parameters:
        company (str): Company name
        df (pd.DataFrame): DataFrame containing company financial data
        max_forecast_years (int): How many years ahead to forecast

    Returns:
        dict or str: Years required and related info, or a message if not forecastable
    """
    # Step 1: Extract valid historical revenue
    company_df = df[(df["company_name"] == company) & df["total_revenue"].notna()]
    if len(company_df) < 3:
        return f"Not enough data to forecast revenue doubling for {company}."

    # Step 2: Prepare the time series
    series = company_df.set_index("year")["total_revenue"].sort_index()
    series.index = pd.PeriodIndex(series.index, freq='Y')

    # Step 3: Establish base and target revenue
    base_revenue = series.iloc[-1]
    target_revenue = base_revenue * 2
    last_year = int(str(series.index[-1]))

    # Step 4: Forecast using Holt’s model
    try:
        model = ExponentialSmoothing(series, trend="add", seasonal=None, initialization_method="estimated")
        fit = model.fit()

        forecast = fit.forecast(max_forecast_years)
        forecast_years = [last_year + i + 1 for i in range(max_forecast_years)]

        # Step 5: Find first year revenue exceeds double
        for year, predicted in zip(forecast_years, forecast):
            if predicted >= target_revenue:
                return {
                    "company": company,
                    "start_revenue": round(base_revenue, 2),
                    "target_revenue": round(target_revenue, 2),
                    "predicted_year": year,
                    "years_to_double": year - last_year
                }

        return f"{company} is not expected to double its revenue within the next {max_forecast_years} years."

    except Exception as e:
        return f"Forecasting error for {company}: {str(e)}"


# 6. When will a company's liabilities exceed its assets (if ever)?
# Strategy:
# - Extract total_assets and total_liabilities history for the company.
# - Drop missing data.
# - Build two separate time series: one for assets, one for liabilities.
# - Fit Holt’s Linear Trend model separately to both series.
# - Forecast future values year-by-year.
# - Find first year where predicted liabilities ≥ predicted assets.

def predict_liabilities_exceed_assets(company, df, max_forecast_years=20):
    """
    Predicts when a company's liabilities will exceed its assets, if at all,
    by forecasting both series independently using Holt’s Linear Trend model.

    Parameters:
        company (str): Company name
        df (pd.DataFrame): Financial data DataFrame
        max_forecast_years (int): Forecast horizon (default 20 years)

    Returns:
        dict or str: Forecast result with crossover year or message if no crossover expected
    """
    # Step 1: Filter data with non-null assets and liabilities
    company_df = df[
        (df["company_name"] == company) &
        df["total_assets"].notna() &
        df["total_liabilities"].notna()
    ]

    if company_df.shape[0] < 3:
        return f"Not enough data to forecast assets vs liabilities for {company}."

    # Step 2: Create time series
    assets_series = company_df.set_index("year")["total_assets"].sort_index()
    liabilities_series = company_df.set_index("year")["total_liabilities"].sort_index()

    # Ensure both indices are PeriodIndex with yearly frequency
    assets_series.index = pd.PeriodIndex(assets_series.index, freq='Y')
    liabilities_series.index = pd.PeriodIndex(liabilities_series.index, freq='Y')

    last_year = max(int(str(assets_series.index[-1])), int(str(liabilities_series.index[-1])))

    # Step 3: Fit Holt models
    try:
        asset_model = ExponentialSmoothing(assets_series, trend="add", seasonal=None, initialization_method="estimated").fit()
        liability_model = ExponentialSmoothing(liabilities_series, trend="add", seasonal=None, initialization_method="estimated").fit()

        forecast_assets = asset_model.forecast(max_forecast_years)
        forecast_liabilities = liability_model.forecast(max_forecast_years)
        forecast_years = [last_year + i + 1 for i in range(max_forecast_years)]

        # Step 4: Find first year liabilities exceed assets
        for year, asset_val, liability_val in zip(forecast_years, forecast_assets, forecast_liabilities):
            if liability_val >= asset_val:
                return {
                    "company": company,
                    "predicted_crossover_year": year,
                    "predicted_liabilities": round(liability_val, 2),
                    "predicted_assets": round(asset_val, 2)
                }

        return f"{company} is not expected to have liabilities exceed assets within the next {max_forecast_years} years."

    except Exception as e:
        return f"Forecasting error for {company}: {str(e)}"


# ====================================
# Group D – Verbal Analysis
# ====================================

# 1. What are the primary revenue streams for the company, and how have they evolved over the past three years?
# Strategy:
# - For the given company and year, look up the field 'revenue_streams_summary' in the metadata table.
# - Return the summary text directly if available.
# - If the field is missing or empty, return an informative message.

def get_revenue_streams_summary(company, year, df):
    """
    Retrieves the pre-written revenue streams summary for a specific company and year.

    Parameters:
        company (str): The company name
        year (int): The fiscal year
        df (pd.DataFrame): The metadata DataFrame

    Returns:
        str: Revenue streams summary or an informative message if unavailable
    """
    row = df[(df["company_name"] == company) & (df["year"] == year)]

    if row.empty:
        return f"No data found for {company} in {year}."

    summary = row.iloc[0].get("revenue_streams_summary", None)

    if pd.isna(summary) or summary is None:
        return f"Revenue streams summary not available for {company} in {year}."

    return summary.strip()


# 2. How diversified is the company's customer base according to the latest 10-K?
# Strategy:
# - Look up the most recent available record for the given company with a non-empty 'customer_base' field.
# - Return the content of that field directly.
# - If no content is available, return an informative message.

def get_customer_base_summary(company, df):
    """
    Returns the most recent 'customer_base' summary for the specified company.

    Parameters:
        company (str): The company name
        df (pd.DataFrame): The metadata DataFrame

    Returns:
        str: Customer base summary or a message if not available
    """
    company_df = df[(df["company_name"] == company) & df["customer_base"].notna()]
    if company_df.empty:
        return f"No customer base information available for {company}."

    # Get the most recent year
    latest_record = company_df.sort_values("year", ascending=False).iloc[0]
    summary = latest_record.get("customer_base", None)

    if pd.isna(summary) or summary is None:
        return f"Customer base summary not available for {company}."

    return summary.strip()



# 3. Identify the main competitors mentioned in the 10-K and explain the competitive landscape.
# Strategy:
# - Look up the most recent available record for the given company with a non-empty 'competitive_landscape' field.
# - Return the content of that field directly.
# - If no content is available, return an informative message.

def get_competitive_landscape(company, year, df):
    """
    Retrieves the competitive landscape summary for a specific company and year.

    Parameters:
        company (str): Company name
        year (int): Fiscal year
        df (pd.DataFrame): The metadata DataFrame

    Returns:
        str: Competitive landscape summary or a message if unavailable
    """
    row = df[(df["company_name"] == company) & (df["year"] == year)]

    if row.empty:
        return f"No data found for {company} in {year}."

    summary = row.iloc[0].get("competitive_landscape", None)

    if pd.isna(summary) or summary is None:
        return f"Competitive landscape summary not available for {company} in {year}."

    return summary.strip()


# 4. How does the company describe its growth strategy and future objectives?
# Strategy:
# - Look up the record for the specified company and year in the 'growth_strategy' column.
# - Return the content of that field directly.
# - If the field is missing or null, return an informative message.

def get_growth_strategy(company, year, df):
    """
    Retrieves the growth strategy summary for a specific company and year.

    Parameters:
        company (str): Company name
        year (int): Fiscal year
        df (pd.DataFrame): Metadata table containing the growth strategy field

    Returns:
        str: Growth strategy summary or a message if unavailable
    """
    row = df[(df["company_name"] == company) & (df["year"] == year)]

    if row.empty:
        return f"No data found for {company} in {year}."

    summary = row.iloc[0].get("growth_strategy", None)

    if pd.isna(summary) or summary is None:
        return f"Growth strategy summary not available for {company} in {year}."

    return summary.strip()



# 5. What major risks or uncertainties did the company highlight,
#    and how significant are these compared to industry standards?
# Strategy:
# - Look up the record for the specified company and year in the 'highlighted_risks' column.
# - Return the content of that field directly.
# - If the field is missing or null, return an informative message.

def get_highlighted_risks(company, year, df):
    """
    Retrieves the highlighted risks summary for a specific company and year.

    Parameters:
        company (str): Company name
        year (int): Fiscal year
        df (pd.DataFrame): Metadata table containing the highlighted risks field

    Returns:
        str: Highlighted risks summary or a message if unavailable
    """
    row = df[(df["company_name"] == company) & (df["year"] == year)]

    if row.empty:
        return f"No data found for {company} in {year}."

    summary = row.iloc[0].get("highlighted_risks", None)

    if pd.isna(summary) or summary is None:
        return f"Highlighted risks summary not available for {company} in {year}."

    return summary.strip()


# 6. Does the company face any notable regulatory challenges,
#    based on recent market trends and information provided?
# Strategy:
# - Look up the record for the specified company and year in the 'regulatory_challenges' column.
# - Return the content of that field directly.
# - If the field is missing or null, return an informative message.

def get_regulatory_challenges(company, year, df):
    """
    Retrieves the regulatory challenges summary for a specific company and year.

    Parameters:
        company (str): Company name
        year (int): Fiscal year
        df (pd.DataFrame): Metadata table containing the regulatory challenges field

    Returns:
        str: Regulatory challenges summary or a message if unavailable
    """
    row = df[(df["company_name"] == company) & (df["year"] == year)]

    if row.empty:
        return f"No data found for {company} in {year}."

    summary = row.iloc[0].get("regulatory_challenges", None)

    if pd.isna(summary) or summary is None:
        return f"Regulatory challenges summary not available for {company} in {year}."

    return summary.strip()



# 7. What is the trend of the company's net income over the last three fiscal years?
# Strategy:
# - Retrieve the value from the 'net_income_trend_summary' field for the specified company and year.
# - Return the summary directly if available.
# - If not available, return a helpful message.

def get_net_income_trend_summary(company, year, df):
    """
    Returns the net income trend summary for a specific company and year.

    Parameters:
        company (str): The company name
        year (int): The fiscal year
        df (pd.DataFrame): The metadata DataFrame

    Returns:
        str: Summary of net income trend or a message if unavailable
    """
    row = df[(df["company_name"] == company) & (df["year"] == year)]

    if row.empty:
        return f"No data found for {company} in {year}."

    summary = row.iloc[0].get("net_income_trend_summary", None)

    if pd.isna(summary) or summary is None:
        return f"Net income trend summary not available for {company} in {year}."

    return summary.strip()



# 8. How does the company's EBITDA margin compare with the industry average?
# Strategy:
# - Look up the record for the specified company and year in the 'ebitda_margin_comparison' column.
# - Return the content of that field directly.
# - If the field is missing or null, return an informative message.

def get_ebitda_margin_comparison(company, year, df):
    """
    Returns the EBITDA margin comparison to industry for a given company and year.

    Parameters:
        company (str): The company name
        year (int): Fiscal year to search for
        df (pd.DataFrame): Metadata table with the field 'ebitda_margin_comparison'

    Returns:
        str: Summary or message if unavailable
    """
    row = df[(df["company_name"] == company) & (df["year"] == year)]

    if row.empty:
        return f"No data found for {company} in {year}."

    summary = row.iloc[0].get("ebitda_margin_comparison", None)

    if pd.isna(summary) or summary is None:
        return f"EBITDA margin comparison not available for {company} in {year}."

    return summary.strip()


# 9. Describe any unusual or significant changes in operating expenses highlighted in the 10-K.
# Strategy:
# - For the given company and year, return the content of 'operating_expense_commentary'.
# - If the field is empty or null, return a helpful message.

def get_operating_expense_commentary(company, year, df):
    """
    Returns the operating expense commentary for a specific company and year.

    Parameters:
        company (str): The name of the company
        year (int): The fiscal year
        df (pd.DataFrame): The DataFrame containing company metadata

    Returns:
        str: Commentary text or an informative message
    """
    row = df[(df["company_name"] == company) & (df["year"] == year)]

    if row.empty:
        return f"No data found for {company} in {year}."

    commentary = row.iloc[0].get("operating_expense_commentary", None)

    if pd.isna(commentary) or commentary is None:
        return f"Operating expense commentary not available for {company} in {year}."

    return commentary.strip()


# 10. Based on current financials and market conditions,
#     what insights can be derived about the company's valuation?
# Strategy:
# - For the given company and year, return the value from 'valuation_commentary'.
# - If the field is missing, empty, or null, return a helpful message instead.

def get_valuation_commentary(company, year, df):
    """
    Returns the valuation commentary for a specific company and year.

    Parameters:
        company (str): Company name
        year (int): Fiscal year
        df (pd.DataFrame): DataFrame containing company metadata

    Returns:
        str: Valuation commentary or an informative fallback message
    """
    row = df[(df["company_name"] == company) & (df["year"] == year)]

    if row.empty:
        return f"No data found for {company} in {year}."

    commentary = row.iloc[0].get("valuation_commentary", None)

    if pd.isna(commentary) or commentary is None:
        return f"Valuation commentary not available for {company} in {year}."

    return commentary.strip()



# 11. What major capital expenditures did the company undertake,
#     and what could be their long-term impacts?
# Strategy:
# - For the given company and year, return the value from 'capital_expenditures_projects'.
# - If the field is missing, empty, or null, return an informative fallback message.

def get_capital_expenditure_projects(company, year, df):
    """
    Returns a summary of capital expenditure projects for a given company and year.

    Parameters:
        company (str): The company name
        year (int): The fiscal year
        df (pd.DataFrame): Metadata table including 'capital_expenditures_projects'

    Returns:
        str: Capital expenditure project description or fallback message
    """
    row = df[(df["company_name"] == company) & (df["year"] == year)]

    if row.empty:
        return f"No data found for {company} in {year}."

    commentary = row.iloc[0].get("capital_expenditures_projects", None)

    if pd.isna(commentary) or commentary is None:
        return f"No capital expenditure project commentary available for {company} in {year}."

    return commentary.strip()


# 12. Can you identify and discuss the company’s current dividend policy
#     or share repurchase strategies?
# Strategy:
# - For the given company and year, return the value from 'dividend_and_buyback_policy'.
# - If the field is missing or empty, return a message indicating no commentary is available.

def get_dividend_and_buyback_policy(company, year, df):
    """
    Retrieves dividend and stock buyback policy commentary for a specific company and year.

    Parameters:
        company (str): Name of the company
        year (int): Fiscal year
        df (pd.DataFrame): DataFrame with metadata including 'dividend_and_buyback_policy'

    Returns:
        str: The dividend/buyback policy commentary or fallback message
    """
    row = df[(df["company_name"] == company) & (df["year"] == year)]

    if row.empty:
        return f"No data found for {company} in {year}."

    commentary = row.iloc[0].get("dividend_and_buyback_policy", None)

    if pd.isna(commentary) or commentary is None:
        return f"No dividend or buyback policy commentary available for {company} in {year}."

    return commentary.strip()


# 13. How effective has the company been at managing inventory and accounts receivable compared to peers?
# Strategy:
# - Retrieve 'days_sales_outstanding' and 'working_capital_efficiency' fields for the given company and year.
# - Use both numeric and narrative data to evaluate working capital effectiveness.

def analyze_working_capital_efficiency(company, year, df):
    """
    Analyzes the company's efficiency in managing working capital (inventory and receivables)
    based on Days Sales Outstanding (DSO) and narrative commentary.

    Parameters:
        company (str): Company name
        year (int): Fiscal year
        df (pd.DataFrame): Financial metadata containing 'days_sales_outstanding' and 'working_capital_efficiency'

    Returns:
        str: Summary of working capital efficiency or fallback message
    """
    row = df[(df["company_name"] == company) & (df["year"] == year)]

    if row.empty:
        return f"No working capital data available for {company} in {year}."

    dso = row.iloc[0].get("days_sales_outstanding", "N/A")
    wc_text = row.iloc[0].get("working_capital_efficiency", None)

    if pd.isna(wc_text) or wc_text is None:
        return f"No working capital commentary available for {company} in {year}."

    context = f"- Year: {year}\n- Days Sales Outstanding (DSO): {dso}\n\n{wc_text.strip()}"
    return context


# 14. Are there any management changes or board restructuring plans mentioned,
#     and what could be their impact?
# Strategy:
# - Look for the 'management_changes' cell for the specified company and year.
# - Use the extracted governance narrative as-is or with minimal formatting.
# - Return a clear, summarized answer or fallback message if no data exists.

def analyze_management_changes(company, year, df):
    """
    Analyzes management or board restructuring changes for a company in a given year.

    Parameters:
        company (str): The company name
        year (int): The fiscal year to analyze
        df (pd.DataFrame): DataFrame with financial metadata including 'management_changes'

    Returns:
        str: Narrative context from the 10-K or a fallback message
    """
    row = df[(df["company_name"] == company) & (df["year"] == year)]

    if row.empty:
        return f"No management or board restructuring data found for {company} in {year}."

    changes = row.iloc[0].get("management_changes", None)
    if pd.isna(changes) or not changes:
        return f"No management or board restructuring data found for {company} in {year}."

    return f"- Year: {year}\n\n{changes.strip()}"


# 15. Did the company experience disruptions in its supply chain,
#     and how does this compare to the broader industry situation?
# Strategy:
# - Use the 'supply_chain_disruptions' cell for the given company and year.
# - Return the raw explanation as reported in the 10-K.
# - If missing, return a clear message indicating unavailability.

def analyze_supply_chain_disruptions(company, year, df):
    """
    Retrieves the supply chain disruption commentary for a given company and year.

    Parameters:
        company (str): The company name
        year (int): The fiscal year to analyze
        df (pd.DataFrame): DataFrame containing financial metadata

    Returns:
        str: Commentary on supply chain issues or fallback message
    """
    row = df[(df["company_name"] == company) & (df["year"] == year)]

    if row.empty:
        return f"No supply chain commentary available for {company} in {year}."

    disruption_info = row.iloc[0].get("supply_chain_disruptions", None)
    if pd.isna(disruption_info) or not disruption_info:
        return f"No supply chain commentary available for {company} in {year}."

    return f"- Year: {year}\n\n{disruption_info.strip()}"


# 16. What ESG initiatives or sustainability practices has the company emphasized in the 10-K?
# Strategy:
# - Use the 'esg_initiatives' cell from the specified company and year.
# - Return the reported sustainability and ESG activities directly from the 10-K data.
# - If no data is available for that year, return a fallback message.

def analyze_esg_initiatives(company, year, df):
    """
    Retrieves ESG initiatives or sustainability practices disclosed in a given year.

    Parameters:
        company (str): Company name
        year (int): Fiscal year
        df (pd.DataFrame): Financial metadata DataFrame

    Returns:
        str: ESG commentary or fallback message
    """
    row = df[(df["company_name"] == company) & (df["year"] == year)]

    if row.empty:
        return f"No ESG or sustainability data found for {company} in {year}."

    esg_data = row.iloc[0].get("esg_initiatives", None)
    if pd.isna(esg_data) or not esg_data:
        return f"No ESG or sustainability disclosures found for {company} in {year}."

    return f"- Year: {year}\n\n{esg_data.strip()}"



# 17. Has the company faced any ESG-related controversies or litigations recently?
# Strategy:
# - Retrieve the 'esg_controversies' cell for the given company and year.
# - If present, return the controversy text as-is from the 10-K metadata table.
# - If not found, return a fallback message.

def analyze_esg_controversies(company, year, df):
    """
    Retrieves ESG-related controversies or litigation details for the specified company and year.

    Parameters:
        company (str): Company name
        year (int): Fiscal year
        df (pd.DataFrame): DataFrame containing metadata with ESG fields

    Returns:
        str: Controversy summary or fallback message
    """
    row = df[(df["company_name"] == company) & (df["year"] == year)]

    if row.empty:
        return f"No ESG-related data found for {company} in {year}."

    controversy = row.iloc[0].get("esg_controversies", None)
    if pd.isna(controversy) or not controversy:
        return f"No ESG-related controversies reported for {company} in {year}."

    return f"- Year: {year}\n\n{controversy.strip()}"



# 18. Describe how the company's governance structure aligns with best practices within its industry.
# Strategy:
# - Retrieve the 'governance_structure' field from the metadata table for the given company and year.
# - Return the governance summary text directly if available.
# - If not found or empty, return a fallback message.

def analyze_governance_structure(company, year, df):
    """
    Extracts governance structure details for a specific company and year.

    Parameters:
        company (str): Company name
        year (int): Fiscal year
        df (pd.DataFrame): Metadata table with governance information

    Returns:
        str: Governance structure summary or fallback message
    """
    row = df[(df["company_name"] == company) & (df["year"] == year)]

    if row.empty:
        return f"No governance structure data found for {company} in {year}."

    governance = row.iloc[0].get("governance_structure", None)
    if pd.isna(governance) or not governance:
        return f"No governance structure description available for {company} in {year}."

    return f"- Year: {year}\n\n{governance.strip()}"


# 19. What is the company's current debt-to-equity ratio,
#     and how sustainable is its debt level?
# Strategy:
# - Retrieve the 'debt_to_equity_ratio' and 'debt_sustainability_commentary' for the given company and year.
# - Return a structured summary that includes both the ratio and commentary.
# - If data is missing, respond with a fallback message.

def analyze_debt_sustainability(company, year, df):
    """
    Analyzes the debt sustainability for a specific company and year.

    Parameters:
        company (str): Company name
        year (int): Fiscal year
        df (pd.DataFrame): Metadata table with debt-related information

    Returns:
        str: Commentary on debt sustainability or fallback message
    """
    row = df[(df["company_name"] == company) & (df["year"] == year)]

    if row.empty:
        return f"No debt-to-equity data found for {company} in {year}."

    ratio = row.iloc[0].get("debt_to_equity_ratio", None)
    commentary = row.iloc[0].get("debt_sustainability_commentary", None)

    if pd.isna(ratio):
        return f"Debt-to-equity ratio not available for {company} in {year}."

    result = f"- Year: {year}\n- Debt-to-Equity Ratio: {ratio:.2f}\n\n"

    if pd.isna(commentary) or not commentary:
        result += "No commentary provided on debt sustainability."
    else:
        result += str(commentary).strip()

    return result


# 20. Has the company recently refinanced or restructured its debt,
#     and if so, what are the implications?
# Strategy:
# - Retrieve the 'debt_refinancing_activity' field for the specified company and year.
# - Return the text explanation of refinancing steps and implications.
# - If no data exists, return a fallback explanation.

def analyze_debt_refinancing(company, year, df):
    """
    Analyzes the company's debt refinancing activity for a given year.

    Parameters:
        company (str): Company name
        year (int): Fiscal year
        df (pd.DataFrame): DataFrame with debt-related fields

    Returns:
        str: Summary of refinancing activity or a fallback message
    """
    row = df[(df["company_name"] == company) & (df["year"] == year)]

    if row.empty:
        return f"No debt refinancing data found for {company} in {year}."

    activity = row.iloc[0].get("debt_refinancing_activity", None)

    if pd.isna(activity) or not activity:
        return f"No commentary on debt refinancing provided by {company} in {year}."

    return str(activity).strip()



# 21. How have recent technological advancements in the industry
#     affected the company's operations?
# Strategy:
# - Retrieve the 'technology_impact_on_operations' field for the specified company and year.
# - If available, return the narrative on how technology has impacted operations.
# - If not available, return a clear fallback message.

def analyze_technology_impact(company, year, df):
    """
    Summarizes how technological trends have affected the company's operations in a given year.

    Parameters:
        company (str): Company name
        year (int): Fiscal year of interest
        df (pd.DataFrame): DataFrame with company disclosures

    Returns:
        str: Narrative explanation or fallback message
    """
    row = df[(df["company_name"] == company) & (df["year"] == year)]

    if row.empty:
        return f"No technology impact data found for {company} in {year}."

    impact = row.iloc[0].get("technology_impact_on_operations", None)

    if pd.isna(impact) or not impact:
        return f"No commentary on technological impact provided by {company} in {year}."

    return str(impact).strip()


# 22. Does the company explicitly mention emerging industry trends
#     or technologies they're investing in?
# Strategy:
# - Use 'emerging_tech_investments' from the specified year.
# - If the field is present, return the investment commentary.
# - Otherwise, return a message stating no disclosure was found.

def analyze_emerging_tech_investments(company, year, df):
    """
    Retrieves information about the company's investments in emerging technologies for a specific year.

    Parameters:
        company (str): Company name
        year (int): Fiscal year of interest
        df (pd.DataFrame): DataFrame with all metadata fields

    Returns:
        str: Emerging tech investment narrative or fallback message
    """
    row = df[(df["company_name"] == company) & (df["year"] == year)]

    if row.empty:
        return f"No emerging technology investment data found for {company} in {year}."

    investment = row.iloc[0].get("emerging_tech_investments", None)

    if pd.isna(investment) or not investment:
        return f"No disclosure on emerging tech investments for {company} in {year}."

    return str(investment).strip()



# 23. What significant patents or intellectual property assets
# Strategy:
# - Extract 'intellectual_property_assets' for the specified company and year.
# - If the field is populated, return the summary directly.
# - Otherwise, indicate that no IP disclosures were found.

def analyze_intellectual_property(company, year, df):
    """
    Returns the intellectual property assets disclosure for a given company and year.

    Parameters:
        company (str): Company name
        year (int): Fiscal year
        df (pd.DataFrame): The final_metadata_table DataFrame

    Returns:
        str: Summary of intellectual property assets or fallback message
    """
    row = df[(df["company_name"] == company) & (df["year"] == year)]

    if row.empty:
        return f"No intellectual property data found for {company} in {year}."

    ip_assets = row.iloc[0].get("intellectual_property_assets", None)

    if pd.isna(ip_assets) or not ip_assets:
        return f"No IP asset disclosure available for {company} in {year}."

    return str(ip_assets).strip()


# 24. Describe the company's investment in R&D compared to industry benchmarks.
# Strategy:
# - Retrieve 'research_and_development_expense', 'research_and_development_investment',
#   and 'research_and_development_commentary' for the specified company and year.
# - Return the numeric values and commentary in structured text format without using an LLM.

def analyze_r_and_d_investment(company, year, df):
    """
    Returns R&D investment figures and commentary for the given company and year.

    Parameters:
        company (str): Company name
        year (int): Fiscal year
        df (pd.DataFrame): DataFrame with company metadata

    Returns:
        str: Summary of R&D investment and commentary
    """
    row = df[(df["company_name"] == company) & (df["year"] == year)]

    if row.empty:
        return f"No R&D investment data available for {company} in {year}."

    record = row.iloc[0]
    r_and_d_expense = record.get("research_and_development_expense")
    r_and_d_investment = record.get("research_and_development_investment")
    r_and_d_commentary = record.get("research_and_development_commentary")

    lines = [f"R&D Investment Report for {company} in {year}:"]
    if pd.notna(r_and_d_expense):
        lines.append(f"- R&D Expense: ${r_and_d_expense:,}")
    else:
        lines.append("- R&D Expense: Not available")

    if pd.notna(r_and_d_investment):
        lines.append(f"- R&D Investment (% of Revenue): {r_and_d_investment:.2f}%")
    else:
        lines.append("- R&D Investment (% of Revenue): Not available")

    if pd.notna(r_and_d_commentary):
        lines.append(f"\nR&D Commentary:\n{r_and_d_commentary}")
    else:
        lines.append("\nNo R&D strategy commentary found in the 10-K.")

    return "\n".join(lines)


# 25. How does the company position its brand in the marketplace,
#     based on information from the 10-K and broader market knowledge?
# Strategy:
# - Retrieve the value in the 'brand_positioning' column for the specified company and year.
# - Return the content directly without involving a language model.

def analyze_brand_positioning(company, year, df):
    """
    Returns the brand positioning text reported by the company in a specific year.

    Parameters:
        company (str): Company name
        year (int): Fiscal year
        df (pd.DataFrame): DataFrame with company metadata

    Returns:
        str: Brand positioning summary or a message if not found
    """
    row = df[(df["company_name"] == company) & (df["year"] == year)]

    if row.empty:
        return f"No data found for {company} in {year}."

    value = row.iloc[0].get("brand_positioning")

    if pd.isna(value) or value in ["", "NULL", None]:
        return f"No brand positioning information available for {company} in {year}."

    return value


# 26. Did the company undergo any rebranding or significant marketing shifts?
# Strategy:
# - Retrieve the 'rebranding_or_marketing_shift' field for the specified company and year.
# - Return the narrative directly without using an LLM.

def analyze_rebranding_or_marketing_shift(company, year, df):
    """
    Returns rebranding or marketing shift narrative for the specified company and year.

    Parameters:
        company (str): Company name
        year (int): Fiscal year
        df (pd.DataFrame): DataFrame with company metadata

    Returns:
        str: Narrative on rebranding/marketing shift or a not-found message
    """
    row = df[(df["company_name"] == company) & (df["year"] == year)]

    if row.empty:
        return f"No rebranding or marketing shift data found for {company} in {year}."

    record = row.iloc[0]
    shift_data = record.get("rebranding_or_marketing_shift")

    if pd.isna(shift_data) or not shift_data:
        return f"No rebranding or marketing shift commentary available for {company} in {year}."

    return f"Rebranding or Marketing Shift for {company} in {year}:\n{shift_data}"


# 27. How sensitive is the company to macroeconomic conditions,
#     such as inflation, interest rate changes, or currency fluctuations?
# Strategy:
# - Retrieve the 'macroeconomic_sensitivity' field for the given company and year.
# - Supplement with 'foreign_revenue_percent' to indicate FX exposure.
# - Return both as a direct summary without using an LLM.

def analyze_macroeconomic_sensitivity(company, year, df):
    """
    Summarizes macroeconomic sensitivity commentary and FX exposure for a company.

    Parameters:
        company (str): Company name
        year (int): Fiscal year
        df (pd.DataFrame): DataFrame containing company data

    Returns:
        str: Summary text or a message if data is unavailable
    """
    row = df[(df["company_name"] == company) & (df["year"] == year)]

    if row.empty:
        return f"No macroeconomic sensitivity data found for {company} in {year}."

    record = row.iloc[0]
    commentary = record.get("macroeconomic_sensitivity")
    fx_percent = record.get("foreign_revenue_percent")

    if pd.isna(commentary) or not commentary:
        return f"No macroeconomic commentary available for {company} in {year}."

    summary = f"Macroeconomic Sensitivity for {company} in {year}:\n{commentary}"
    if pd.notna(fx_percent):
        summary += f"\n\nForeign Revenue Exposure: {fx_percent:.2f}%"

    return summary


# 28. Has the company described any direct impacts from global geopolitical events or economic shifts?
# Strategy:
# - Retrieve the 'geopolitical_and_economic_impacts' field for the specified company and year.
# - Return the content directly without using an LLM.

def analyze_geopolitical_and_economic_impacts(company, year, df):
    """
    Returns the company's disclosed geopolitical and economic impact narrative for a specific year.

    Parameters:
        company (str): Company name
        year (int): Fiscal year
        df (pd.DataFrame): DataFrame containing company disclosures

    Returns:
        str: Summary or disclosure text, or message if not found
    """
    row = df[(df["company_name"] == company) & (df["year"] == year)]

    if row.empty:
        return f"No geopolitical or economic impact disclosures found for {company} in {year}."

    value = row.iloc[0].get("geopolitical_and_economic_impacts")

    if pd.isna(value) or not value:
        return f"No geopolitical or economic impact data provided for {company} in {year}."

    return f"Geopolitical and Economic Impacts for {company} in {year}:\n{value}"



# 29. Based on current financials and market conditions,
#     what are plausible growth scenarios for the company over the next three years?
# Strategy:
# - Retrieve the 'growth_scenarios' field for the specified company and year.
# - Return its contents directly as the analysis answer.

def analyze_growth_scenarios(company, year, df):
    """
    Returns the plausible growth scenarios disclosed by the company for a specific year.

    Parameters:
        company (str): Company name
        year (int): Fiscal year
        df (pd.DataFrame): Full metadata DataFrame

    Returns:
        str: Growth scenario description or message if not available
    """
    row = df[(df["company_name"] == company) & (df["year"] == year)]

    if row.empty:
        return f"No growth scenario data available for {company} in {year}."

    value = row.iloc[0].get("growth_scenarios")

    if pd.isna(value) or not value:
        return f"No growth scenario commentary found for {company} in {year}."

    return f"Plausible Growth Scenarios for {company} in {year}:\n{value}"


# 30. What forward-looking statements or future commitments did the company emphasize,
#     and how realistic are these in the context of current market conditions?
# Strategy:
# - Retrieve the 'forward_looking_statement' field for the specified company and year.
# - Return its contents directly as the answer.

def analyze_forward_looking_statements(company, year, df):
    """
    Returns the forward-looking statements made by a company in a specific year.

    Parameters:
        company (str): Company name
        year (int): Fiscal year
        df (pd.DataFrame): The full metadata DataFrame

    Returns:
        str: Forward-looking statements text or a message if unavailable
    """
    row = df[(df["company_name"] == company) & (df["year"] == year)]

    if row.empty:
        return f"No forward-looking statement data available for {company} in {year}."

    value = row.iloc[0].get("forward_looking_statement")

    if pd.isna(value) or not value:
        return f"No forward-looking statement commentary found for {company} in {year}."

    return f"Forward-Looking Statements for {company} in {year}:\n{value}"