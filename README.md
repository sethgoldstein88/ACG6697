# UMD Audit Analysis

Comprehensive data analysis for the Urgent Medical Device (UMD) audit case, examining potential revenue fraud in fiscal year 2017.

## Overview

This project analyzes UMD's sales, shipments, invoices, and customer data to identify fraud risk factors and control failures in the revenue recognition process for fiscal year 2017.

**Trial Balance Amounts:**
- Sales Revenue: $84,867,855
- Accounts Receivable: $11,988,886
- Allowance for Doubtful Accounts: $315,000

## Repository Structure

```
📁 notebooks/          # Analysis notebooks (01-06)
📁 data/              # Source Excel files (6 datasets)
📁 outputs/
  ├── tables/         # CSV files with detailed findings
  └── figures/        # Charts and visualizations
```

## How to Use This Repository

### For Memo Writers

**Each notebook answers one specific requirement:**

1. Open any notebook (click on `.ipynb` files in `notebooks/` folder)
2. **Scroll to TOP** → See "ANSWER TO REQUIREMENT" section with key findings
3. **Scroll to BOTTOM** → See "Summary & Audit Implications" section
4. Download supporting files from `outputs/` folder as needed

**You don't need to run any code - just read the notebooks!**

### Notebooks Overview

| Notebook | Requirement | Key Finding |
|----------|-------------|-------------|
| `02_fraud_risk_factors.ipynb` | Req 1: Fraud Risk Factors | Bill-and-hold, cutoff manipulation, management override |
| `02_reconciliation.ipynb` | Req 2: Revenue/AR Reconciliation | 1,158 records = $84.9M; 148 invoices = $12M AR |
| `03_three_way_match.ipynb` | Req 3: Three-Way Match | 2 exceptions: $171K invoiced but not shipped |
| `04_credit_analysis.ipynb` | Req 4-5: Credit Limits | No violations found (but 22 limits increased in Q4) |
| `05_aging_analysis.ipynb` | Req 6: Aging Analysis | 5 invoices >90 days; allowance inadequate |
| `06_fraud_detection.ipynb` | Req 7: Additional Analysis | Dec 31 concentration, credit manipulation |

## Key Findings Summary

### Critical Issues Identified:

1. **Three-Way Match Failures**
   - 2 invoices ($171,080) recognized without shipment
   - Both on December 31, 2017 (cutoff manipulation)

2. **Period-End Revenue Stuffing**
   - $1.8M in revenue (2.1% of total) recorded on December 31 alone
   - Pattern consistent with channel stuffing

3. **Credit Limit Manipulation**
   - 22 distributors (30% of customer base) had credit limits increased in Q4 2017
   - Explains why no "over limit" exceptions found

4. **Collection Risk**
   - 31 invoices ($2.6M) remain completely unpaid
   - 148 invoices ($12M) outstanding at year-end

5. **Inadequate Allowance**
   - Current allowance: $315,000
   - Recommended based on aging: $707,000
   - Shortfall: $392,000

### Audit Assertions at Risk:

- ❌ **Existence/Occurrence** - Failed (invoiced but not shipped)
- ❌ **Cutoff** - Failed (December 31 concentration)
- ⚠️ **Valuation** - Concern (inadequate allowance)
- ✅ **Accuracy** - Passed (reconciliation complete)

## Output Files

### Tables (CSV format in `outputs/tables/`)

Ready to import into Excel or Word:
- `invoiced_not_shipped.csv` - Critical exceptions
- `three_way_match_exceptions.csv` - All match failures
- `high_risk_customers.csv` - Collection risk analysis
- `aging_over_90_days.csv` - Past due invoices
- `q4_credit_limit_changes.csv` - Suspicious limit increases
- ...and 14 more detailed analysis files

### Figures (PNG format in `outputs/figures/`)

Professional visualizations ready for presentation:
- `fraud_analysis.png` - Fraud pattern overview
- `three_way_match_exceptions.png` - Exception analysis
- `aging_analysis.png` - AR aging distribution
- `credit_analysis.png` - Credit utilization
- `period_end_revenue.png` - Q4 revenue patterns

## Data Sources

All analysis based on 6 Excel files in `data/` folder:
- Sales Orders (1,168 records)
- Shipments (1,165 records)
- Customer Invoices (1,167 records)
- Customer Master (73 distributors)
- Sales Territory (5 territories)
- Products (14 SKUs)

## Quick Reference: What to Use Where

**For the main memo findings:**
- Start with `notebooks/00_findings_summary.md` for complete overview
- Reference specific notebooks for detailed analysis

**For exception lists:**
- Use CSV files from `outputs/tables/`

**For visual support:**
- Use PNG charts from `outputs/figures/`

**For understanding methodology:**
- Read the analysis sections within each notebook

## Questions?

- See `umdcase.md` for case background and requirements
- Check `notebooks/README.md` for notebook usage guide
- Review `notebooks/00_findings_summary.md` for complete findings reference

---

**Note:** This is an academic project for educational purposes. All data and analysis relate to a fictional audit case.
