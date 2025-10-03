# Notebook Verification Report
**Date:** October 3, 2025  
**Purpose:** Verify correctness of all notebooks after fixing IsPaid field in data_loader.py

---

## Summary of data_loader.py Fix

**Issue:** The `IsPaid` field was being calculated AFTER `PaidDate` was converted to datetime, causing the string comparison `str.startswith("9999")` to fail. This resulted in ALL invoices being marked as paid (IsPaid=True), even those with PaidDate="9/9/9999".

**Fix Applied:** Line 310-312 now correctly calculates `IsPaid` BEFORE datetime conversion:
```python
df["IsPaid"] = df["PaidDate"].notna() & ~df["PaidDate"].astype(str).str.startswith("9999")
```

**Verification:** 
- Total invoices: 1,167
- IsPaid = True: 1,130 (paid invoices)
- IsPaid = False: 37 (unpaid invoices, PaidDate = "9/9/9999")
- AR Balance: $11,988,886.08 (matches trial balance within $0.08)

---

## Notebook-by-Notebook Analysis

### 1. notebooks/01_data_loading.ipynb ✓ CORRECT
**Status:** No issues found  
**Dependencies:** Does not use IsPaid field  
**Action:** None required

---

### 2. notebooks/02_reconciliation.ipynb ✓ CORRECT
**Status:** Now producing correct results with updated data_loader.py  
**Key Outputs (Verified):**
- Revenue: $84,867,855.00 (matches trial balance)
- AR: $11,988,886.08 (matches trial balance within $0.08)
- Outstanding invoices: 148 (31 unpaid + 117 paid in 2018)

**Dependencies:** Uses IsPaid logic indirectly through string comparison  
**Action:** No changes needed - notebook is correct and produces accurate results

---

### 3. notebooks/03_three_way_match.ipynb ✓ CORRECT
**Status:** No issues found  
**Dependencies:** Does not use IsPaid field  
**Action:** None required

---

### 4. notebooks/04_credit_analysis.ipynb ⚠️ REQUIRES UPDATE
**Status:** MARKDOWN ANSWER SECTION IS INCORRECT  
**Issue:** The markdown answer cells at the top of the notebook state "NO EXCEPTIONS FOUND" but the actual computational results correctly show "EXCEPTIONS FOUND: 2 customers"

**Correct Computational Results (Verified):**
- Requirement 4: NO EXCEPTIONS (all sales have credit limits) ✓
- Requirement 5: **EXCEPTIONS FOUND: 2 customers exceeding credit limits**
  - Customer ID 16: AR = $750,000, Credit Limit = $500,000, Over by $250,000
  - Customer ID 42: AR = $496,946, Credit Limit = $250,000, Over by $246,946
  - Total amount over limit: $496,945.99

**Current Answer Section (Lines 11-27):** States "NO EXCEPTIONS FOUND" for Requirement 5  
**Action Required:** Update markdown answer section to reflect correct findings

---

### 5. notebooks/05_aging_analysis.ipynb ✓ CORRECT
**Status:** Now producing correct results with updated data_loader.py  
**Key Outputs (Verified):**
- AR outstanding: 148 invoices
- Still unpaid: 31 invoices
- Paid in 2018: 117 invoices
- Total AR: $11,988,886.08

**Dependencies:** Uses IsPaid field via PaidDate=NaT check  
**Action:** No changes needed - notebook is correct and produces accurate results

---

### 6. notebooks/06_fraud_detection.ipynb ✓ CORRECT
**Status:** No issues found  
**Dependencies:** Does not use IsPaid field  
**Action:** None required

---

### 7. notebooks/04_credit_analysis_check.ipynb ⚠️ OUTDATED
**Status:** Contains old/incorrect results  
**Issue:** Shows 0 unpaid invoices (should be 31)  
**Action:** This appears to be a test/duplicate file. Can be deleted or ignored.

---

## Summary of Required Actions

### CRITICAL (Must Fix):
1. **notebooks/04_credit_analysis.ipynb** - Update markdown answer section for Requirement 5
   - Change from "NO EXCEPTIONS FOUND" to "EXCEPTIONS FOUND: 2 customers"
   - Add details about Customer IDs 16 and 42
   - Update key findings section

2. **notebooks/00_findings_summary.md**   - Update credit analysis section
   - Change Requirement 5 from "NO EXCEPTIONS" to "EXCEPTIONS FOUND: 2 customers"

### OPTIONAL:
3. **notebooks/04_credit_analysis_check.ipynb** - Delete or re-run (appears to be a test file)

---

## Notebooks That Are CORRECT:
- 01_data_loading.ipynb ✓
- 02_reconciliation.ipynb ✓
- 03_three_way_match.ipynb ✓
- 05_aging_analysis.ipynb ✓
- 06_fraud_detection.ipynb ✓

---

## Data Integrity Confirmation

All notebooks were re-executed with the fixed data_loader.py and produce consistent results:
- 2017 Revenue: $84,867,855.00 (matches trial balance)
- 2017 AR: $11,988,886.08 (matches trial balance)
- Unpaid invoices: 37 (31 from 2017, 6 from 2016)
- 2017 unpaid invoices: 31
- Total AR invoices as of 12/31/17: 148 (31 unpaid + 117 paid in 2018)

The fix to data_loader.py has resolved the IsPaid field issue without introducing any new problems.

