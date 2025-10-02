# UMD Audit Case - Project Context & Guidelines

## Project Overview

This is the **UMD (Urgent Medical Device) audit case** - an academic group project where I am performing data analysis to support my teammates in writing a professional audit memo. The case involves analyzing revenue and accounts receivable for potential fraud in fiscal year 2017.

## Required Context Files

When working on this project, **always** have access to:

1. **`PROJECT_CONTEXT.md`** (this file) - Structure, standards, deliverables
2. **`umdcase.md`** - Case background, requirements, data dictionary
3. **`data/` folder** - Source Excel files

Without umdcase.md, the agent won't understand:

- Business context (fraud risks, pressure to meet targets)
- Specific requirement questions to answer
- Data definitions (what does PaidDate = 9/9/9999 mean?)
- Audit implications (why bill-and-hold matters)

## Key Constraint: Analysis for Non-Technical Teammates

**My teammates need to write a professional audit memo but should NOT need to:**

- Run or understand Python code
- Debug notebooks
- Figure out what findings mean
- Hunt through cells to find answers

**They MUST be able to:**

- Open a notebook and immediately see the answer to that requirement
- Copy/paste exception lists into their memo
- Use pre-generated visualizations
- Understand the business significance of findings
- Trace findings back to methodology if needed

## Required Structure: Multiple Focused Notebooks (Self-Contained)

### Directory Structure

```
notebooks/
  ├── 01_data_loading.ipynb           ← Data quality verification
  ├── 02_reconciliation.ipynb         ← Requirement 2 (COMPLETE with findings)
  ├── 03_three_way_match.ipynb        ← Requirement 3 (COMPLETE with findings)
  ├── 04_credit_analysis.ipynb        ← Requirements 4 & 5 (COMPLETE with findings)
  ├── 05_aging_analysis.ipynb         ← Requirement 6 (COMPLETE with findings)
  └── 06_fraud_detection.ipynb        ← Requirement 7 (COMPLETE with findings)

outputs/
  ├── tables/                          ← CSV files ready for memo
  └── figures/                         ← Publication-ready visualizations

src/
  └── [helper functions if needed]
```

**Philosophy:** Each notebook is SELF-CONTAINED. A teammate should be able to open notebook 03 and immediately find the answer to Requirement 3 without opening any other files.

### Notebook Standards

**Critical:** Use the `edit_notebook` tool to create/edit notebooks.

Each notebook MUST be self-contained and answer its requirement completely. Structure:

1. **Header Section (Markdown Cell at Top) - THE ANSWER**

   ```markdown
   # Requirement X: [Title]
   
   ---
   
   ## 📋 ANSWER TO REQUIREMENT
   
   **[Direct answer to the case question in 2-3 sentences]**
   
   ### Key Findings:
   - Finding 1: [Specific number/count + business significance]
   - Finding 2: [Specific number/count + business significance]
   - Finding 3: [Pattern identified]
   
   ### Recommended Actions:
   - [What should auditors do next?]
   
   ---
   
   ## Data Sources
   - [Which Excel files used]
   
   ## Outputs Generated
   - outputs/tables/[filename].csv
   - outputs/figures/[filename].png
   ```

2. **Analysis Sections**

   - Clear markdown headers for each analytical step
   - Code cells with inline comments explaining logic
   - **Markdown cells AFTER each major analysis step interpreting results**
   - Don't just show DataFrames - explain what they mean in audit terms

3. **Footer Section**

   ```markdown
   ## 📊 Summary & Audit Implications
   
   [2-3 paragraphs explaining]:
   - What the data shows
   - Why this matters for the audit (which assertions affected)
   - What the pattern suggests about fraud risk
   - What further testing is recommended
   ```

**The teammate should be able to scroll to the top and bottom of the notebook to get everything they need for the memo WITHOUT reading code.**

## Output File Standards

### CSV Files (outputs/tables/)

- Include column headers
- Sort by significance (highest $ amount first, or most suspicious)
- Include enough context columns (CustomerID, InvoiceID, Amount, Date, etc.)
- No raw Python index columns
- Ready to import into Word/Excel

### Figures (outputs/figures/)

- High DPI (300) for print quality
- Clear titles and axis labels
- Audit-appropriate styling (professional, not flashy)
- Include source note if relevant
- File naming: descriptive (e.g., `q4_revenue_spike_by_territory.png`)

## Code Quality Standards

1. **Pandas Best Practices**

   - Use clear variable names (not `df1`, `df2`)
   - Chain operations when readable
   - Add comments for complex logic
   - Handle missing data explicitly

2. **Reproducibility**

   - All notebooks should run top-to-bottom without errors
   - Use relative paths from project root
   - Don't hard-code values that come from data
   - Clear any notebook output before committing (optional)

3. **Documentation**
   - Explain WHY, not just WHAT
   - Interpret results in business terms
   - Call out audit implications

## Data Files Location

All source data is in `data/` directory:

- `UMD_Data Set_Sales Orders.xlsx`
- `UMD_Data Set_Shipments.xlsx`
- `UMD_Data Set_Customer Invoices.xlsx`
- `UMD_Data Set_Customer Master.xlsx`
- `UMD_Data Set_Sales Territory.xlsx`
- `UMD_Data Set_Products.xlsx`

## Case Requirements Summary

See `umdcase.md` for full details. Key deliverables:

1. Identify 3 fraud risk factors (6 pts)
2. Data reconciliation - tie to trial balance (8 pts)
3. Three-way match analysis (6 pts)
4. Sales without credit limits (4 pts)
5. AR exceeding credit limits (6 pts)
6. Aging analysis - compare to client's list (12 pts)
7. Additional fraud analysis (24 pts)
8. Who to interview? (4 pts)

**Total: 70 points**

## When Helping Me:

### DO:
✅ Put the ANSWER at the top of each notebook (in markdown)
✅ Create outputs (CSV, figures) that teammates can directly use
✅ Explain findings in audit/business terms within the notebook
✅ Generate clear visualizations with context
✅ Identify patterns and explain their significance
✅ Add interpretation markdown cells after major analysis steps
✅ Save all outputs to appropriate directories
✅ Include a summary section at the bottom of each notebook

### DON'T:
❌ Create notebooks without clear findings at the top
❌ Generate code without interpretation
❌ Leave findings as "there's an anomaly" without business context
❌ Assume teammates will read the code to understand results
❌ Make assumptions about fraud without evidence
❌ Forget to save tables/figures to outputs/
❌ Try to maintain a separate summary document (focus on the notebook itself)

## Success Criteria

The project is successful when my teammates can:

1. Open notebook 02, scroll to the top, and immediately see the answer to Requirement 2
2. Copy specific numbers, patterns, and insights from notebook headers/footers into their memo
3. Insert professional visualizations from `outputs/figures/`
4. Understand the audit significance without reading any Python code
5. Complete their memo without asking me "what did you find for requirement X?"

**Each notebook should tell a complete story: Question → Analysis → Answer → Implications**

---

**Remember:** This is an AUDIT case. Findings should be:

- Specific (numbers, dates, customer IDs)
- Evidence-based (traceable to data)
- Professionally communicated (appropriate for stakeholders)
- Risk-focused (what assertions are affected, what could go wrong)
