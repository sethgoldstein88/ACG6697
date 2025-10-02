# UMD Audit Analysis

Comprehensive data analysis for the Urgent Medical Device (UMD) audit case, examining potential revenue fraud in fiscal year 2017.

## Project Overview

This project analyzes sales, shipments, invoices, and customer data to identify fraud risk factors and control failures in UMD's revenue recognition process. The analysis supports an academic audit memo examining $84.9M in revenue and $12M in accounts receivable.

## Key Findings

- **Three-Way Match Exceptions**: 2 invoices totaling $171K recognized without shipment
- **Period-End Revenue Concentration**: $1.8M (2.1% of revenue) recorded on December 31 alone
- **Credit Limit Manipulation**: 22 distributors (30%) had limits increased in Q4 2017
- **Collection Risk**: 31 invoices ($2.6M) remain completely unpaid
- **Inadequate Allowance**: Current reserve $315K vs. recommended $707K

## Project Structure

```
notebooks/
  ├── 01_data_loading.ipynb           # Data quality verification
  ├── 02_fraud_risk_factors.ipynb     # Req 1: Fraud risk identification
  ├── 02_reconciliation.ipynb         # Req 2: Revenue & AR reconciliation
  ├── 03_three_way_match.ipynb        # Req 3: Orders-Shipments-Invoices match
  ├── 04_credit_analysis.ipynb        # Req 4-5: Credit limit testing
  ├── 05_aging_analysis.ipynb         # Req 6: Aging & allowance adequacy
  └── 06_fraud_detection.ipynb        # Req 7: Additional fraud analysis

data/
  └── [6 Excel files with source data]

outputs/
  ├── tables/    # CSV exception lists and analysis results
  └── figures/   # Professional visualizations
```

## How to Use

**For Memo Writers (Non-Technical):**
1. Open any notebook in GitHub (click on `.ipynb` files above)
2. Scroll to the TOP → See "📋 ANSWER TO REQUIREMENT" section
3. Scroll to the BOTTOM → See "📊 Summary & Audit Implications"
4. Download CSV/PNG files from `outputs/` folder as needed

**For Analysts (To Re-Run):**
```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/umd-audit-analysis.git
cd umd-audit-analysis

# Install dependencies
uv sync

# Run notebooks
jupyter notebook
```

## Requirements Analysis

| Requirement | Notebook | Status | Key Finding |
|-------------|----------|--------|-------------|
| 1. Fraud Risk Factors | `02_fraud_risk_factors.ipynb` | ✅ Complete | 3 factors: Bill-and-hold, cutoff manipulation, management override |
| 2. Revenue/AR Reconciliation | `02_reconciliation.ipynb` | ✅ Complete | 1,158 records = $84.9M revenue; 148 invoices = $12M AR |
| 3. Three-Way Match | `03_three_way_match.ipynb` | ✅ Complete | 2 exceptions: $171K invoiced but not shipped |
| 4. Sales w/o Credit Limits | `04_credit_analysis.ipynb` | ✅ Complete | No exceptions found |
| 5. AR Exceeding Limits | `04_credit_analysis.ipynb` | ✅ Complete | No exceptions (but 22 limits increased in Q4) |
| 6. Aging Analysis | `05_aging_analysis.ipynb` | ✅ Complete | 5 invoices >90 days; allowance inadequate |
| 7. Additional Fraud Analysis | `06_fraud_detection.ipynb` | ✅ Complete | Period-end stuffing, credit manipulation detected |

## Key Technologies

- **Python 3.13** - Data analysis
- **Pandas** - Data manipulation
- **Jupyter** - Interactive notebooks
- **Matplotlib/Seaborn** - Visualizations

## Audit Assertions Tested

- ✅ **Existence/Occurrence** - Failed (invoiced but not shipped)
- ✅ **Cutoff** - Failed (Dec 31 concentration)
- ✅ **Valuation** - Concern (inadequate allowance)
- ✅ **Accuracy** - Passed (reconciliation complete)

## Documentation

- `PROJECT_CONTEXT.md` - Project guidelines and structure
- `umdcase.md` - Case background and requirements
- `BEST_SHARING_METHOD.md` - How to share this project
- `notebooks/00_findings_summary.md` - Quick reference for all findings

## License

Academic project for educational purposes.

## Contributors

Seth Goldstein - Data Analysis

