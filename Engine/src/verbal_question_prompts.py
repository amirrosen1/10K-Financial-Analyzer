PROMPT_REVENUE_STREAMS = """
You are a financial analyst. Below is a summary of revenue-related information from a company’s 10-K reports over the past three years.

This summary includes passages describing the company’s revenue streams (such as products, services, business units, or regions), as well as the total net sales for each year.

Based on the content and your knowledge of financial reporting, please answer the following:

**Question:** What are the company's primary revenue streams, and how have they evolved over the past three years?

**Context:**
{context}

**Answer:**
"""


PROMPT_CUSTOMER_BASE = """
You are analyzing a company's financial disclosures. Below is an excerpt from the company's latest 10-K report describing its customer base.

Your task is to determine how diversified the customer base is. Consider whether the company depends on a few large customers, sells broadly across many markets, or targets specific industries or geographies.

Base your answer both on the information provided and your general understanding of business models.

**Question:** How diversified is the company's customer base according to the latest 10-K?

**Context:**
{context}

**Answer:**
"""


PROMPT_COMPETITIVE_LANDSCAPE = """
You are analyzing a company's 10-K report. The following passage describes aspects of the competitive landscape in which the company operates.

Your task is to identify the company’s main competitors (if mentioned), and explain how the company positions itself in the market. Consider factors such as market share, product differentiation, pricing, or barriers to entry if relevant.

**Question:** Who are the main competitors, and what is the company's competitive position?

**Context:**
{context}

**Answer:**
"""


PROMPT_GROWTH_STRATEGY = """
You are analyzing a company’s strategic outlook based on its most recent 10-K filing.

The following text summarizes how the company describes its growth strategy and future objectives. Your task is to explain the key initiatives or goals the company is pursuing, such as product development, market expansion, partnerships, or innovation.

**Question:** How does the company describe its growth strategy and future objectives?

**Context:**
{context}

**Answer:**
"""


PROMPT_HIGHLIGHTED_RISKS = """
You are analyzing a company's risk disclosures in its most recent 10-K filing.

The following excerpt contains the company’s description of major risks or uncertainties. Your task is to summarize the key risks and assess how significant they are in comparison to what is typical for the industry.

Use both the context provided and your general business knowledge of industry norms when making your assessment.

**Question:** What major risks or uncertainties did the company highlight, and how significant are these compared to industry standards?

**Context:**
{context}

**Answer:**
"""


PROMPT_REGULATORY_CHALLENGES = """
You are analyzing a company’s recent 10-K disclosures to evaluate regulatory risks.

The following passage contains statements related to legal and regulatory challenges the company has reported. Your task is to determine whether the company is currently facing any significant regulatory issues, and comment on how these risks compare to current market trends or industry norms.

Base your answer both on the text and your broader knowledge of regulatory trends.

**Question:** Does the company face any notable regulatory challenges, based on recent market trends and information provided?

**Context:**
{context}

**Answer:**
"""


PROMPT_NET_INCOME_TREND = """
You are a financial analyst. The table below shows the company's net income and fiscal year end date over the past five years.

Your task is to describe the overall trend in net income — whether it has increased, decreased, fluctuated, or remained relatively stable — and provide a brief interpretation of the financial trajectory.

**Question:** What is the trend of the company’s net income over the last five fiscal years?

**Context (Net Income Trend Table):**
{context}

**Answer:**
"""


PROMPT_EBITDA_COMPARISON = """
You are a financial analyst. Below is the company's EBITDA margin for a specific year, as well as a description of the company's sector.

Using both the provided margin and your general knowledge of industry norms, determine whether the company's EBITDA margin is above, below, or close to the industry average. Include reasoning and a brief explanation.

**Question:** How does the company's EBITDA margin compare with the industry average?

**Context:**
{context}

**Answer:**
"""


PROMPT_OPERATING_EXPENSE_COMBINED = """
You are analyzing a company’s recent 10-K disclosures. The table below shows operating expense trends over the past few years, followed by management’s own commentary on the changes.

Your task is to describe any unusual or significant changes in operating expenses. Use both the numerical trend and the company’s explanation to support your analysis.

**Question:** Describe any unusual or significant changes in operating expenses highlighted in the 10-K.

**Context:**
{context}

**Answer:**
"""


PROMPT_VALUATION_COMBINED = """
You are analyzing a company’s valuation based on its most recent 10-K disclosures.

Below is a snapshot of selected financial metrics, followed by commentary extracted from the report. Use both the numbers and the narrative to explain how investors might value this company. Consider profitability, spending efficiency, growth potential, and investor sentiment.

**Question:** Based on current financials and market conditions, what insights can be derived about the company's valuation?

**Context:**
{context}

**Answer:**
"""


PROMPT_CAPITAL_EXPENDITURE_ANALYSIS = """
You are analyzing a company’s capital expenditures from its most recent 10-K filing.

The table below shows the capital expenditure value, and the following commentary describes how the company spent it. Your task is to summarize the major CapEx areas and reason about their potential long-term impact on operations, efficiency, growth, or valuation.

**Question:** What major capital expenditures did the company undertake, and what could be their long-term impacts?

**Context:**
{context}

**Answer:**
"""


PROMPT_DIVIDEND_POLICY = """
You are analyzing a company's shareholder return strategy based on its most recent 10-K filing.

The information below includes financial data on dividends and share repurchases, as well as narrative excerpts from the report. Your task is to summarize the company’s current dividend policy or buyback strategy, and explain what this reveals about its approach to capital allocation and investor relations.

**Question:** Can you identify and discuss the company’s current dividend policy or share repurchase strategies?

**Context:**
{context}

**Answer:**
"""


PROMPT_WORKING_CAPITAL_RECEIVABLES = """
You are evaluating a company's ability to manage its accounts receivable and inventory based on its most recent 10-K report.

The table below shows the company's Days Sales Outstanding (DSO), and the commentary describes aspects of working capital and operational efficiency. Use this information to evaluate how well the company manages collections and inventory turnover, especially in comparison to typical industry performance.

**Question:** How effective has the company been at managing inventory and accounts receivable compared to peers?

**Context:**
{context}

**Answer:**
"""


PROMPT_MANAGEMENT_CHANGES = """
You are analyzing a company’s recent 10-K report to assess leadership changes.

The following excerpts describe changes in executive leadership or board restructuring. Your task is to summarize what changes occurred and provide an assessment of how these changes may affect company direction, investor confidence, or strategic outcomes.

**Question:** Are there any management changes or board restructuring plans mentioned, and what could be their impact?

**Context:**
{context}

**Answer:**
"""


PROMPT_SUPPLY_CHAIN_DISRUPTIONS = """
You are analyzing a company’s recent 10-K filing to assess supply chain risk.

The following excerpts describe the company’s experience with supply chain issues. Your task is to summarize whether the company experienced disruptions, and evaluate whether these challenges appear unique or consistent with industry-wide trends.

**Question:** Did the company experience disruptions in its supply chain, and how does this compare to the broader industry situation?

**Context:**
{context}

**Answer:**
"""


PROMPT_ESG_INITIATIVES = """
You are analyzing a company’s recent 10-K report for ESG (Environmental, Social, Governance) disclosures.

The following excerpts summarize the company's stated sustainability practices and ESG-related efforts. Your task is to list the key initiatives and explain the areas of focus (e.g., emissions, diversity, governance, ethics), as well as the overall tone or commitment level shown by the company.

**Question:** What ESG initiatives or sustainability practices has the company emphasized in the 10-K?

**Context:**
{context}

**Answer:**
"""


PROMPT_ESG_CONTROVERSIES = """
You are reviewing a company’s recent 10-K disclosures to identify potential ESG-related controversies or litigations.

The context below includes excerpts from the Legal Proceedings and Risk Factors sections. Based on this information and your broader understanding of ESG risks, determine whether the company has faced any recent controversies or legal actions related to environmental, social, or governance issues.

**Question:** Has the company faced any ESG-related controversies or litigations recently?

**Context:**
{context}

**Answer:**
"""


PROMPT_GOVERNANCE_STRUCTURE = """
You are analyzing the company’s corporate governance structure based on its most recent 10-K report.

The context below describes the company’s board composition, committee structure, and governance practices. Your task is to assess how well these align with industry best practices, including board independence, diversity, executive roles, and shareholder protections.

**Question:** Describe how the company's governance structure aligns with best practices within its industry.

**Context:**
{context}

**Answer:**
"""


PROMPT_DEBT_SUSTAINABILITY = """
You are analyzing the financial health of a company based on its most recent 10-K filing.

Below is the company’s debt-to-equity ratio and additional commentary related to its debt structure and capital management. Assess how sustainable the company’s current debt level is, and whether the debt-to-equity ratio aligns with industry expectations for its sector.

**Question:** What is the company's current debt-to-equity ratio, and how sustainable is its debt level?

**Context:**
{context}

**Answer:**
"""


PROMPT_DEBT_REFINANCING = """
You are analyzing a company's recent 10-K disclosure to evaluate its debt refinancing activity.

The excerpts below describe actions related to refinancing, restructuring, or repaying debt. Your task is to summarize what actions were taken, and explain the potential financial or strategic implications — such as improved liquidity, interest savings, risk reduction, or shareholder impact.

**Question:** Has the company recently refinanced or restructured its debt, and if so, what are the implications?

**Context:**
{context}

**Answer:**
"""


PROMPT_TECHNOLOGY_IMPACT = """
You are analyzing a company’s most recent 10-K filing to assess how technological advancements in the industry have affected its operations.

The excerpts below describe the company's use of new technologies or its response to evolving digital trends. Your task is to summarize how industry-wide technological changes have impacted the company’s internal operations — including areas such as efficiency, innovation, cost structure, supply chain, or workforce.

**Question:** How have recent technological advancements in the industry affected the company's operations?

**Context:**
{context}

**Answer:**
"""


PROMPT_EMERGING_TECH_INVESTMENTS = """
You are analyzing a company’s most recent 10-K report to identify forward-looking investments.

The following excerpts describe technologies and trends mentioned by the company. Your task is to determine whether the company is explicitly investing in or aligning with emerging technologies or industry trends, and if so, which ones.

**Question:** Does the company explicitly mention emerging industry trends or technologies they're investing in?

**Context:**
{context}

**Answer:**
"""


PROMPT_INTELLECTUAL_PROPERTY = """
You are analyzing a company’s most recent 10-K disclosures to understand its intellectual property position.

The excerpts below describe the company’s ownership of patents or other IP assets. Your task is to summarize which significant IP assets are owned or were recently acquired, and explain how these assets may relate to the company's core business or competitive advantage.

**Question:** What significant patents or intellectual property assets does the company own or has recently acquired?

**Context:**
{context}

**Answer:**
"""


PROMPT_R_AND_D_FIELD_ALIGNED = """
You are evaluating a company’s R&D strategy based on its most recent 10-K report.

Below is a snapshot of its R&D expense and investment ratio, followed by management commentary. Compare the company’s investment level to what is typical in its industry, and summarize whether the company appears to be under-investing, over-investing, or aligned with peers.

**Question:** Describe the company's investment in R&D compared to industry benchmarks.

**Context:**
{context}

**Answer:**
"""


PROMPT_BRAND_POSITIONING = """
You are analyzing a company’s brand positioning based on its most recent 10-K report, along with your broader market understanding.

The excerpts below describe how the company portrays its brand, value proposition, and market role. Summarize how the company is positioning its brand in the marketplace and assess whether this positioning aligns with broader industry perception or strategic objectives.

**Question:** How does the company position its brand in the marketplace, based on information from the 10-K and broader market knowledge?

**Context:**
{context}

**Answer:**
"""


PROMPT_REBRANDING_ACTIVITY = """
You are analyzing a company's most recent 10-K report to determine if it has made any significant changes to its branding or marketing strategy.

The excerpts below describe marketing-related disclosures. Your task is to summarize whether the company has undergone rebranding or changed how it presents itself to customers. Include any marketing strategy shifts, new messaging, or changes in brand identity.

**Question:** Did the company undergo any rebranding or significant marketing shifts according to its disclosures?

**Context:**
{context}

**Answer:**
"""


PROMPT_MACROECONOMIC_SENSITIVITY_MINIMAL = """
You are analyzing a company’s exposure to macroeconomic risks based on its most recent 10-K report.

The data below includes the company’s foreign revenue exposure and qualitative commentary about macroeconomic conditions. Use this to evaluate how sensitive the company is to inflation, interest rate changes, and currency volatility, and whether that sensitivity is above or below industry norms.

**Question:** How sensitive is the company to macroeconomic conditions, such as inflation, interest rate changes, or currency fluctuations?

**Context:**
{context}

**Answer:**
"""


PROMPT_GEOPOLITICAL_IMPACTS = """
You are analyzing a company’s 10-K report to identify whether global geopolitical or economic events have directly impacted its operations or strategy.

The excerpts below describe any relevant statements. Your task is to summarize what global events were mentioned and how they directly affected the company — such as through supply chains, regulation, revenue, inflation, or cost structure.

**Question:** Has the company described any direct impacts from global geopolitical events or economic shifts?

**Context:**
{context}

**Answer:**
"""


PROMPT_GROWTH_SCENARIOS = """
You are a strategic financial analyst. Based on the company’s most recent 10-K and current market dynamics, your task is to describe plausible growth scenarios for the company over the next three years.

The data includes key financial metrics and commentary on growth strategies, risks, and investments. Based on this, provide a range of potential growth trajectories (e.g., baseline, optimistic, cautious), and explain the assumptions behind each.

**Question:** Based on current financials and market conditions, what are plausible growth scenarios for the company over the next three years?

**Context:**
{context}

**Answer:**
"""


PROMPT_FORWARD_LOOKING_EVALUATION = """
You are analyzing a company’s forward-looking statements from its most recent 10-K report.

The excerpts below summarize future-oriented claims or goals stated by the company. Your task is to identify the key commitments and evaluate how realistic or achievable they are, given current market conditions, competitive pressures, and economic trends.

**Question:** What forward-looking statements or future commitments did the company emphasize in the latest 10-K, and how realistic are these in the context of current market conditions?

**Context:**
{context}

**Answer:**
"""