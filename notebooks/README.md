# UMD Audit Analysis - Notebooks

## 🎯 For Memo Writers: How to Use These Notebooks

**Each notebook is SELF-CONTAINED and answers one requirement completely.**

### How to Find Answers:
1. **Open the notebook for your requirement** (e.g., `03_three_way_match.ipynb` for Requirement 3)
2. **Scroll to the TOP** → Read the "📋 ANSWER TO REQUIREMENT" section
3. **Scroll to the BOTTOM** → Read the "📊 Summary & Audit Implications" section
4. **Copy findings directly into your memo** (numbers, patterns, recommendations)
5. **Use output files** from `outputs/tables/` and `outputs/figures/`

**You should NEVER need to read the Python code to understand the findings.**

---

## 📊 Analysis Notebooks

Each notebook contains: The Question → The Analysis → The Answer → The Implications

- **`01_data_loading.ipynb`** - Data quality verification (optional reference)
- **`02_reconciliation.ipynb`** - ✅ Requirement 2: Revenue & AR reconciliation
- **`03_three_way_match.ipynb`** - ✅ Requirement 3: Orders → Shipments → Invoices match
- **`04_credit_analysis.ipynb`** - ✅ Requirements 4 & 5: Credit limit issues
- **`05_aging_analysis.ipynb`** - ✅ Requirement 6: Aging analysis
- **`06_fraud_detection.ipynb`** - ✅ Requirement 7: Additional fraud analysis

### 📁 Supporting Files

- **`../outputs/tables/`** - CSV files with exception lists (import to Excel/Word)
- **`../outputs/figures/`** - Professional charts and graphs (insert in memo)

---

## Workflow

```
1. Analyst creates self-contained notebooks (02 → 06)
   ↓
2. Each notebook has findings at top & bottom
   ↓
3. Each notebook generates outputs/
   ↓
4. Memo writer opens notebooks + reads findings
   ↓
5. Memo gets written! 
```

---

## How to Use These Notebooks

### If You're the Analyst:

1. Run notebooks in order (01 → 06)
2. **Put findings at TOP of each notebook** (in markdown)
3. **Put summary at BOTTOM of each notebook** (audit implications)
4. Generate outputs (tables/figures) as you go
5. Make sure findings are specific with numbers and patterns
6. Explain everything in business/audit terms


---

## Case Requirements Checklist

- [ ] Req 1: Identify 3 fraud risk factors (6 pts)
- [ ] Req 2a: Count of sales records = $84,867,855 (4 pts)
- [ ] Req 2b: Count of unpaid invoices = $11,988,886 (4 pts)
- [ ] Req 3: Three-way match exceptions (6 pts)
- [ ] Req 4: Sales without credit limits (4 pts)
- [ ] Req 5: AR exceeding credit limits (6 pts)
- [ ] Req 6a: Aging analysis vs. client's list (4 pts)
- [ ] Req 6b: Sufficiency of allowance + concerns (8 pts)
- [ ] Req 7a: Plan for additional analysis (12 pts)
- [ ] Req 7b: Conduct analysis + findings (12 pts)
- [ ] Req 8: Who to interview? (4 pts)

**Total: 70 points**

---

## Quick Tips

### For Analysis Quality:

 Be specific (numbers, dates, customer IDs)
 Explain patterns (not just "there are exceptions")
 Consider audit implications (what assertions are at risk?)
 Suggest next steps (what further testing is needed?)

### For Memo Writing:

 Use professional audit language
 Reference specific evidence (tables, figures)
 Connect findings to fraud risks
 Be objective but direct about concerns

---

## Questions?

- Check `PROJECT_CONTEXT.md` in the root directory for full guidelines
- Review `umdcase.md` for case background and requirements
- Ask your analyst teammate if findings need clarification!
