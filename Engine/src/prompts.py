EXTRACT_FIELD_v1 = """
You are an expert in Information extraction in 10-K documents.
You are given a 10-K file and your job is to extract the relevant field that answers the given the query:
<query>
You must return the output in a valid JSON in the following format:
{
    'answer' : '<extracted_answer>'
}
If the data is missing return null in the extracted answer value.
If the query is regarding money, include the currency.
This is the document:
<document>
"""

EXTRACT_FIELD = """
        ### Financial Report Extraction ###
        Document:
        <document_content>
        Instruction: Extract the answer to the following query:
        "<query>"
        Respond ONLY in **valid JSON** format, like this:
        {{
          "query": "<query>",
          "answer": "<extracted_value or null>"
        }}
        - If the answer is not available in the document, return "answer": null.
        - Do not include any text outside the JSON.
        - Ensure the JSON is well-formed and parsable.
        Answer:
        """

OLD_PROMPT = """
f"### Financial Report Extraction ###\n"
f"Document:\n{document_content}\n\n"
f"Instruction: Extract the Total revenue or Total net sales for the year {year}. "
f"Respond ONLY in the format: 'Total net sales ({year}): $X'. "
f"If the data is missing, return: 'Total net sales ({year}): null'.\n\n"
f"Answer:"
"""


EXTRACT_FIELD_TEMPLATE = (
    f"### Financial Report Analysis ###\n\n"
    f"Query:\n<query>\n\n"
    f"Document Context:\n<document>\n\n"
    f"Instructions:\n"
    f"- Provide the most accurate and complete answer to the query, based on the document.\n"
    f"- You may summarize, infer, or rephrase as needed, as long as the answer is grounded in the content.\n"
    f"- Do NOT include reasoning, explanations, or commentary before or after the answer.\n"
    f"- If the answer is not available or cannot be determined, return exactly: N/A\n\n"
    f"Answer:"
)



EXTRACT_FIELD_TEMPLATE_NUMERIC = (
    f"### Financial Field Extraction Task ###\n\n"
    f"Your job is to extract a single numeric value (with correct scale, if mentioned) from a 10-K financial document.\n\n"
    f"Query:\n<query>\n\n"
    f"Document:\n<document>\n\n"
    f"Instructions:\n"
    f"- Extract the exact number that answers the query.\n"
    f"- If the number has a scale like \"million\", \"billion\", or uses symbols like \"$\", include them.\n"
    f"- The value must come from official financial tables (e.g., Income Statement, Balance Sheet).\n"
    f"- If multiple years are mentioned, choose the value for the year referenced in the query.\n"
    f"- Do NOT return any labels, units (e.g., USD), or explanations — only the value.\n"
    f"- Do NOT explain the reasoning or return full sentences.\n"
    f"- If the answer is not found, return exactly: N/A\n\n"
    f"Format:\n"
    f"<value> ← Just the number, possibly with \"million\"/\"billion\" or currency symbol.\n\n"
    f"Examples:\n"
    f"- 10,300\n"
    f"- $2.5 billion\n"
    f"- N/A\n\n"
    f"Answer:"
)

EXTRACT_COMPANY_YEAR_PROMPT = """
Extract the company name and the filing year from the first page of this 10-K form.

Return your answer in the following JSON format:
{
  "company_name": "<company name>",
  "year": <year>
}

10-K first page:
<page>
"""

EXTRACT_COMPANY_NAME_PROMPT_v1 = """
Given the first page of a 10-K form, extract the official name of the company that filed it.
Return ONLY the name, with no extra explanation.

Text:
<page>
"""

EXTRACT_COMPANY_NAME_PROMPT = """
f"### 10-K Entity Extraction ###\n"
f"Document:\n<page>\n\n"
f"Instruction: Extract the official name of the company that filed this 10-K report.\n"
f"Respond ONLY in the format: 'Company Name: X'.\n"
f"If the name is missing or unclear, return: 'Company Name: null'.\n\n"
f"Answer:"
"""

EXTRACT_FILING_YEAR_PROMPT_v1 = """
Given the first page of a 10-K form, what is the filing year of the report?

Return ONLY the 4-digit year (e.g., 2022). Do not include any text, explanation, or extra formatting.

First page:
<page>
"""

EXTRACT_FILING_YEAR_PROMPT = """
f"### 10-K Entity Extraction ###\n"
f"Document:\n<page>\n\n"
f"Instruction: Extract the filing year — the year the report was submitted to the SEC.\n"
f"Respond ONLY in the format: 'Filing Year: 2022'.\n"
f"If the year is not found, return: 'Filing Year: null'.\n\n"
f"Answer:"
"""

EXTRACT_SECTOR_PROMPT = """
### Sector Identification Task ###

You are analyzing a company's 10-K filing.

Your job is to identify the business sector or industry the company operates in, based on the document context.

Document:
<document>

Instructions:
- Return only the **name of the sector or industry** the company belongs to (e.g., Technology, Finance, Energy, Retail, Healthcare).
- The response must be **short and specific**, with no full sentences.
- Do not include extra commentary, labels, or explanation.
- If the sector is not clearly stated or cannot be inferred from the document, return exactly: N/A

Format:
<sector>

Examples:
- Technology
- Financial Services
- Consumer Goods
- N/A
"""

EXTRACT_TOTAL_REVENUE_PROMPT = EXTRACT_FIELD_TEMPLATE_NUMERIC.replace(
    "<query>", "What is the total revenue for the year <year>?") \
    .replace("<instructions>", "Return only the number. If currency is mentioned, include it. Do not include any text, labels, or formatting. If not found, return 'N/A'.")

EXTRACT_NET_INCOME_PROMPT = EXTRACT_FIELD_TEMPLATE_NUMERIC.replace(
    "<query>", "What is the net income for the year <year>?") \
    .replace("<instructions>", "Return only the number. If currency is mentioned, include it. Do not include any text, labels, or formatting. If not found, return 'N/A'.")

EXTRACT_EPS_PROMPT = EXTRACT_FIELD_TEMPLATE_NUMERIC.replace(
    "<query>", "What is the earnings per share (EPS) for the year <year>?") \
    .replace("<instructions>", "Return only the number. Do not include any text, units, or formatting. If not found, return 'N/A'.")

EXTRACT_OPERATING_INCOME_PROMPT = EXTRACT_FIELD_TEMPLATE_NUMERIC.replace(
    "<query>", "What is the operating income for the year <year>?") \
    .replace("<instructions>", "Return only the number. If currency is mentioned, include it. Do not include any text, labels, or formatting. If not found, return 'N/A'.")

EXTRACT_GROSS_PROFIT_PROMPT = EXTRACT_FIELD_TEMPLATE_NUMERIC.replace(
    "<query>", "What is the gross profit for the year <year>?") \
    .replace("<instructions>", "Return only the number. If currency is mentioned, include it. Do not include any text, labels, or formatting. If not found, return 'N/A'.")

EXTRACT_CASH_FLOW_OPERATING_ACTIVITIES_PROMPT = EXTRACT_FIELD_TEMPLATE_NUMERIC.replace(
    "<query>", "What is the cash flow from operating activities for the year <year>?") \
    .replace("<instructions>", "Return only the number. If currency is mentioned, include it. Do not include any text, labels, or formatting. If not found, return 'N/A'.")

EXTRACT_CAPITAL_EXPENDITURES_PROMPT = EXTRACT_FIELD_TEMPLATE_NUMERIC.replace(
    "<query>", "What are the capital expenditures for the year <year>?") \
    .replace("<instructions>", "Return only the number. If currency is mentioned, include it. Do not include any text, labels, or formatting. If not found, return 'N/A'.")

EXTRACT_TOTAL_ASSETS_PROMPT = EXTRACT_FIELD_TEMPLATE_NUMERIC.replace(
    "<query>", "What are the total assets for the year <year>?") \
    .replace("<instructions>", "Return only the number. If currency is mentioned, include it. Do not include any text, labels, or formatting. If not found, return 'N/A'.")

EXTRACT_TOTAL_LIABILITIES_PROMPT = EXTRACT_FIELD_TEMPLATE_NUMERIC.replace(
    "<query>", "What are the total liabilities for the year <year>?") \
    .replace("<instructions>", "Return only the number. If currency is mentioned, include it. Do not include any text, labels, or formatting. If not found, return 'N/A'.")

EXTRACT_SALES_AND_MARKETING_EXPENSE_PROMPT = EXTRACT_FIELD_TEMPLATE_NUMERIC.replace(
    "<query>", "What are the sales and marketing expenses for the year <year>?") \
    .replace("<instructions>", "Return only the number. If currency is mentioned, include it. Do not include any text, labels, or formatting. If not found, return 'N/A'.")

EXTRACT_SG_A_EXPENSE_PROMPT = EXTRACT_FIELD_TEMPLATE_NUMERIC.replace(
    "<query>", "What is the selling, general and administrative (SG&A) expense for the year <year>?") \
    .replace("<instructions>", "Return only the number. If currency is mentioned, include it. Do not include any text, labels, or formatting. If not found, return 'N/A'.")

EXTRACT_STOCK_ISSUANCE_PROMPT = EXTRACT_FIELD_TEMPLATE_NUMERIC.replace(
    "<query>", "What is the total value of stock issuance for the year <year>?") \
    .replace("<instructions>", "Return only the number. If currency is mentioned, include it. Do not include any text, labels, or formatting. If not found, return 'N/A'.")

EXTRACT_STOCK_REPURCHASES_PROMPT = EXTRACT_FIELD_TEMPLATE_NUMERIC.replace(
    "<query>", "What is the total value of stock repurchases for the year <year>?") \
    .replace("<instructions>", "Return only the number. If currency is mentioned, include it. Do not include any text, labels, or formatting. If not found, return 'N/A'.")

EXTRACT_FISCAL_YEAR_END_PROMPT = EXTRACT_FIELD_TEMPLATE.replace(
    "<query>", "What is the fiscal year-end date for the company in the year <year>?"
).replace(
    "<instructions>", "Return only the date in a concise format like 'December 31'."
)

EXTRACT_OPERATING_EXPENSES_PROMPT = EXTRACT_FIELD_TEMPLATE_NUMERIC.replace(
    "<query>", "What are the total operating expenses for the year <year>?") \
    .replace("<instructions>", "Return only the number. If currency is mentioned, include it. Do not include any text, labels, or formatting. If not found, return 'N/A'.")

EXTRACT_DIVIDENDS_PAID_PROMPT = EXTRACT_FIELD_TEMPLATE_NUMERIC.replace(
    "<query>", "What is the total amount of dividends paid in the year <year>?") \
    .replace("<instructions>", "Return only the number. If currency is mentioned, include it. Do not include any text, labels, or formatting. If not found, return 'N/A'.")

EXTRACT_ACCOUNTS_RECEIVABLE_PROMPT = EXTRACT_FIELD_TEMPLATE_NUMERIC.replace(
    "<query>", "What is the total accounts receivable from the balance sheet for the year <year>? Exclude net or adjusted values.") \
    .replace("<instructions>", "Return only the number. If currency is mentioned, include it. Do not include any text, labels, or formatting. If not found, return 'N/A'.")

EXTRACT_SHAREHOLDER_EQUITY_PROMPT = EXTRACT_FIELD_TEMPLATE_NUMERIC.replace(
    "<query>", "What is the shareholder equity reported in the year <year>?") \
    .replace("<instructions>", "Return only the number. If currency is mentioned, include it. Do not include any text, labels, or formatting. If not found, return 'N/A'.")

EXTRACT_RESEARCH_AND_DEVELOPMENT_EXPENSE_PROMPT = EXTRACT_FIELD_TEMPLATE_NUMERIC.replace(
    "<query>", "What is the research and development (R&D) expense for the year <year>?") \
    .replace("<instructions>", "Return only the number. If currency is mentioned, include it. Do not include any text, labels, or formatting. If not found, return 'N/A'.")

EXTRACT_RESEARCH_AND_DEVELOPMENT_INVESTMENT_PROMPT = EXTRACT_FIELD_TEMPLATE_NUMERIC.replace(
    "<query>", "How much did the company invest in research and development (R&D) during the year <year>?") \
    .replace("<instructions>", "Return only the number. If currency is mentioned, include it. Do not include any text, labels, or formatting. If not found, return 'N/A'.")

EXTRACT_FOREIGN_REVENUE_PROMPT = EXTRACT_FIELD_TEMPLATE_NUMERIC.replace(
    "<query>", "What is the total foreign or international revenue reported for the year <year>?") \
    .replace("<instructions>", "Return only the number. If currency is mentioned, include it. Do not include any text, labels, or formatting. If not found, return 'N/A'.")


# ====================================
# Verbal Prompts
# ====================================

EXTRACT_REVENUE_STREAMS_PROMPT = """
You are an expert in financial analysis of 10-K reports.

The following is context extracted from a 10-K document for the year <year> for <company_name>.

Your task is to answer:
"What are the primary revenue streams for <company_name>, and how have they evolved over the past three years (<year>, <year_minus_1>, <year_minus_2>)?"

Please provide a concise summary using the information from the text.

Context:
<document>

Instructions:
- Focus on identifying distinct sources of revenue.
- Discuss any growth, decline, or shifts mentioned across the years.
- If only the current year is discussed in the text, clearly state that.
- Do not speculate beyond the provided text.

Return the answer in plain text.
"""

EXTRACT_CUSTOMER_BASE_PROMPT = EXTRACT_FIELD_TEMPLATE.replace(
    "<query>",
    "Based on <company_name>’s most recent 10-K filing, describe the diversity and composition of its customer base. Mention if the company relies heavily on a few major customers or if it has a broad and diversified customer base."
).replace(
    "<instructions>",
    "Answer in 2-3 sentences. Be concise, but capture any key figures or customer concentration if mentioned."
)

EXTRACT_COMPETITIVE_LANDSCAPE_PROMPT = EXTRACT_FIELD_TEMPLATE.replace(
    "<query>",
    "Based on <company_name>’s most recent 10-K filing, identify its primary competitors and summarize the competitive landscape. Mention how the company differentiates itself and any trends or risks related to competition."
).replace(
    "<instructions>",
    "Answer in 2-4 sentences. Be specific if competitors are named and include any industry context provided."
)

EXTRACT_GROWTH_STRATEGY_PROMPT = EXTRACT_FIELD_TEMPLATE.replace(
    "<query>",
    "Based on <company_name>’s latest 10-K filing, summarize its growth strategy and key objectives for the future. Highlight specific initiatives, markets, or product plans if mentioned."
).replace(
    "<instructions>",
    "Answer in 2-4 sentences. Use bullet points if it improves clarity."
)

EXTRACT_HIGHLIGHTED_RISKS_PROMPT = EXTRACT_FIELD_TEMPLATE.replace(
    "<query>",
    "What major risks or uncertainties did <company_name> highlight in the year <year>, and how significant are these compared to industry standards?"
).replace(
    "<instructions>",
    "Summarize clearly and concisely. Mention whether the risks are general or specific to the company. Avoid generic statements."
)

EXTRACT_REGULATORY_CHALLENGES_PROMPT = EXTRACT_FIELD_TEMPLATE.replace(
    "<query>",
    "Summarize the notable regulatory challenges <company_name> faced in <year>, especially in relation to evolving market trends or compliance issues."
).replace(
    "<instructions>",
    "Be specific. Focus on challenges that are explicitly mentioned or implied in the document. Avoid generic regulatory language unless clearly relevant."
)

EXTRACT_NET_INCOME_TREND_PROMPT = EXTRACT_FIELD_TEMPLATE \
    .replace("<query>", "Analyze how <company_name>'s net income has changed over the past three years (<year_minus_2>, <year_minus_1>, <year>). The reported net income values are: <year_minus_2>: <net_income_y2>, <year_minus_1>: <net_income_y1>, <year>: <net_income_y3>. Use the document to support your commentary if possible.") \
    .replace("<instructions>", "Summarize the trend clearly in 2-3 sentences. State whether net income is increasing, decreasing, or fluctuating. Mention any notable commentary from the document that may explain these changes.")


EXTRACT_EBITDA_MARGIN_PROMPT = EXTRACT_FIELD_TEMPLATE.replace("<query>", "Based on <company_name>’s 10-K for <year>, what can be inferred about its EBITDA margin and how it compares to industry benchmarks?") \
                                                  .replace("<instructions>", "Summarize the margin and any comparison noted in the document.")

EXTRACT_OPERATING_EXPENSE_COMMENTARY_PROMPT = EXTRACT_FIELD_TEMPLATE \
    .replace("<query>", "Summarize any significant or unusual trends in <company_name>’s operating expenses in <year>. Use this figure if available: <operating_expenses>.") \
    .replace("<instructions>", "Base your answer only on the text provided. Return a short paragraph.")

EXTRACT_VALUATION_COMMENTARY_PROMPT = EXTRACT_FIELD_TEMPLATE \
    .replace("<query>", "Based on <company_name>’s reported financial metrics for <year> — including total revenue: <total_revenue>, net income: <net_income>, operating income: <operating_income>, sales & marketing expense: <sales_and_marketing_expense>, EPS: <eps>, total assets: <total_assets>, stock issuance: <stock_issuance>, and stock repurchases: <stock_repurchases> — summarize any insights or commentary about the company’s valuation.") \
    .replace("<instructions>", "Return a short paragraph based only on the document content.")

EXTRACT_CAPEX_PROJECTS_PROMPT = EXTRACT_FIELD_TEMPLATE \
    .replace("<query>", "Based on <company_name>’s 10-K report for <year>, and given that capital expenditures were reported as <capital_expenditures>, identify any major capital expenditure projects mentioned. What are their expected long-term impacts on the company’s operations or growth?") \
    .replace("<instructions>", "Return a concise paragraph describing the key capital expenditures and their implications.")

EXTRACT_DIVIDEND_AND_BUYBACK_POLICY_PROMPT = EXTRACT_FIELD_TEMPLATE \
    .replace("<query>",
        "Based on the 10-K filing for <year>, what is <company_name>'s current dividend distribution policy or share buyback strategy? "
        "Use these figures if helpful — dividends paid: <dividends_paid>, stock repurchases: <stock_repurchases>, stock issuance: <stock_issuance>.") \
    .replace("<instructions>",
        "Return a short paragraph. If the company does not pay dividends or conduct buybacks, say so. "
        "Highlight if there’s a shift in policy or a preference between dividends vs. buybacks.")

EXTRACT_WORKING_CAPITAL_EFFICIENCY_PROMPT = EXTRACT_FIELD_TEMPLATE \
    .replace("<query>", "Based on the 10-K filing for <year>, how does <company_name> describe its efficiency in managing working capital—particularly inventory and accounts receivable? Use the provided days sales outstanding figure: <days_sales_outstanding>. Compare to industry practices if mentioned.") \
    .replace("<instructions>", "Summarize in 2–4 sentences. Be specific about receivables/inventory management and whether any peer comparison is provided.")

EXTRACT_MANAGEMENT_CHANGES_PROMPT = EXTRACT_FIELD_TEMPLATE \
    .replace("<query>", "In <company_name>’s 10-K filing for <year>, identify any changes in executive leadership, management team, or board structure. If such changes are reported, summarize them and describe any stated or likely impacts on the company.") \
    .replace("<instructions>", "Return a short paragraph summarizing the management or board changes and their potential implications.")

EXTRACT_SUPPLY_CHAIN_DISRUPTIONS_PROMPT = EXTRACT_FIELD_TEMPLATE \
    .replace("<query>", "Based on the company’s 10-K filing for <year>, did <company_name> report any supply chain disruptions? If so, describe the nature and causes. How does this compare to disruptions reported across the broader industry, if mentioned?") \
    .replace("<instructions>", "Answer in 2–4 sentences. Be specific about the disruptions, causes (e.g., pandemic, shipping delays), and any comparison to the industry or peers.")

EXTRACT_ESG_INITIATIVES_PROMPT = EXTRACT_FIELD_TEMPLATE \
    .replace("<query>", "According to <company_name>’s 10-K filing for <year>, identify the key Environmental, Social, and Governance (ESG) initiatives or sustainability practices discussed. Focus on specific programs, policies, goals, or achievements the company emphasized.") \
    .replace("<instructions>", "Return a short paragraph summarizing the company's key ESG or sustainability practices.")

EXTRACT_ESG_CONTROVERSIES_PROMPT = EXTRACT_FIELD_TEMPLATE \
    .replace("<query>", "Based on <company_name>’s 10-K filing for <year>, identify any ESG-related controversies, investigations, or litigations disclosed in the document. Focus on issues related to environmental violations, labor disputes, governance failures, or public criticism.") \
    .replace("<instructions>", "Return a short summary of any ESG-related controversies or write 'None reported' if none are disclosed.")

EXTRACT_GOVERNANCE_STRUCTURE_PROMPT = EXTRACT_FIELD_TEMPLATE \
    .replace("<query>", "Summarize <company_name>’s governance structure as described in the 10-K for <year>. Highlight whether it includes standard best practices such as independent board members, separation of CEO and Chair roles, audit committees, and diversity disclosures. Comment on how this compares to typical governance standards in its industry.") \
    .replace("<instructions>", "Provide a concise paragraph summary.")

EXTRACT_DEBT_SUSTAINABILITY_COMMENTARY_PROMPT = EXTRACT_FIELD_TEMPLATE \
    .replace("<query>", "According to the 10-K report for <year>, and considering that <company_name> has a debt-to-equity ratio of <debt_to_equity_ratio>, analyze how sustainable its current debt level appears. Refer to any relevant debt management strategies or financial risks discussed in the document.") \
    .replace("<instructions>", "Summarize in 2–3 sentences. Use context from the filing. If no commentary is present, respond 'No sustainability assessment discussed explicitly.'")


EXTRACT_DEBT_REFINANCING_ACTIVITY_PROMPT = EXTRACT_FIELD_TEMPLATE \
    .replace("<query>", "Has <company_name> refinanced or restructured its debt in <year> as reported in the 10-K? If yes, explain the nature of the activity (e.g., bond issuance, loan renegotiation) and summarize the financial or strategic implications.") \
    .replace("<instructions>", "Provide a concise summary paragraph. If no refinancing is reported, respond with 'N/A'.")

EXTRACT_TECHNOLOGY_IMPACT_ON_OPERATIONS_PROMPT = EXTRACT_FIELD_TEMPLATE \
    .replace("<query>", "According to the 10-K report for <year>, how have recent technological advancements in the industry impacted <company_name>'s operations or business model? Focus on mentions of automation, digitalization, AI, or supply chain tech.") \
    .replace("<instructions>", "Summarize in 2–3 sentences. Use specific examples if available in the document. If no discussion is provided, say 'No direct mention of technology impact.'")

EXTRACT_EMERGING_TECH_INVESTMENTS_PROMPT = EXTRACT_FIELD_TEMPLATE \
    .replace("<query>", "According to the company's 10-K, did <company_name> mention any emerging technologies or industry trends it is actively investing in? Focus on areas such as AI, automation, cloud, digital platforms, or sustainability tech.") \
    .replace("<instructions>", "Summarize in 2–3 sentences. Mention specific technologies or trends if available. If no such investments are mentioned, respond with 'No specific emerging tech investments disclosed.'")

EXTRACT_IP_ASSETS_PROMPT = EXTRACT_FIELD_TEMPLATE \
    .replace("<query>", "Based on the 10-K filing for <year>, describe any significant patents, trademarks, copyrights, or other intellectual property (IP) assets that <company_name> owns or has acquired. Focus on those highlighted as strategically important or recently obtained.") \
    .replace("<instructions>", "Summarize in 2-3 sentences. Mention specific asset types if possible.")

EXTRACT_R_AND_D_COMMENTARY_PROMPT = EXTRACT_FIELD_TEMPLATE \
    .replace("<query>", "Based on the company's 10-K for <year>, how does <company_name> describe its research and development efforts? Include commentary on R&D spending (<rd_expense>) and investments (<rd_investment>) if available, along with focus areas or innovation goals.") \
    .replace("<instructions>", "Summarize in 2–4 sentences. Mention whether R&D is increasing/decreasing, what it's focused on (e.g., product development, AI, sustainability), and any strategic priorities.")

EXTRACT_BRAND_POSITIONING_PROMPT = EXTRACT_FIELD_TEMPLATE \
    .replace("<query>", "Based on the 10-K filing for <year>, how does <company_name> describe or suggest its brand positioning within the market? Focus on any statements about brand identity, target audience, differentiation, or reputation.") \
    .replace("<instructions>", "Summarize in 2-3 sentences. Be specific about how the company presents itself to customers and the market.")

EXTRACT_REBRANDING_OR_MARKETING_SHIFT_PROMPT = EXTRACT_FIELD_TEMPLATE \
    .replace("<query>", "Based on the company's 10-K report for <year>, did <company_name> report or suggest any significant rebranding efforts or changes in marketing strategy? Include any updates to brand identity, campaigns, or messaging.") \
    .replace("<instructions>", "Summarize in 2-3 sentences. Be specific. If no rebranding or marketing shift is mentioned, say 'No major rebranding or marketing shifts reported.'")

EXTRACT_MACROECONOMIC_SENSITIVITY_PROMPT = EXTRACT_FIELD_TEMPLATE \
    .replace("<query>", "Based on the company's 10-K filing for <year>, how does <company_name> describe its sensitivity to macroeconomic conditions such as inflation, interest rate changes, or currency fluctuations? Consider that foreign revenue comprises <foreign_revenue_percent>% of total revenue.") \
    .replace("<instructions>", "Summarize in 2–4 sentences. Focus on inflation, interest rates, currency risks, and other macro factors. Mention whether the company provides specific commentary or just general sensitivity.")

EXTRACT_GEOPOLITICAL_AND_ECONOMIC_IMPACTS_PROMPT = EXTRACT_FIELD_TEMPLATE \
    .replace("<query>", "Based on the 10-K filing for <year>, did <company_name> report any direct effects from global geopolitical events or macroeconomic shifts such as inflation, interest rates, supply chain issues, or trade restrictions?") \
    .replace("<instructions>", "Summarize clearly in 2-3 sentences. Include examples if stated. If no such impacts are mentioned, say 'No significant geopolitical or economic impacts reported.'")

EXTRACT_GROWTH_SCENARIOS_PROMPT = EXTRACT_FIELD_TEMPLATE \
    .replace("<query>", """Based on the following financial and strategic context from the 10-K for <company_name> (<year>), describe plausible growth scenarios for the next three fiscal years.

Quantitative indicators:
- Revenue: <total_revenue>
- Net Income: <net_income>
- Operating Income: <operating_income>
- R&D Expense: <research_and_development_expense>
- Capital Expenditures: <capital_expenditures>
- Stock Repurchases: <stock_repurchases>
- Foreign Revenue %: <foreign_revenue_percent>

Qualitative context:
<growth_strategy>

Additional insights:
- Macroeconomic Sensitivity: <macroeconomic_sensitivity>
- Emerging Tech Investments: <emerging_tech_investments>
- Valuation Commentary: <valuation_commentary>
- Operating Expense Commentary: <operating_expense_commentary>""") \
    .replace("<instructions>", "Summarize in 3-5 sentences. Outline best-case, moderate, and risk-sensitive scenarios if appropriate. Avoid speculation beyond the text.")

EXTRACT_FORWARD_LOOKING_STATEMENT_PROMPT = EXTRACT_FIELD_TEMPLATE \
    .replace("<query>", "In the 10-K report for <year>, what forward-looking statements or strategic future goals did <company_name> highlight? Evaluate how realistic or grounded these statements appear based on the current market environment and challenges mentioned in the report.") \
    .replace("<instructions>", "Summarize in 2-4 sentences. Focus on statements about future performance, goals, or expectations. If possible, include commentary on realism based on context.")
