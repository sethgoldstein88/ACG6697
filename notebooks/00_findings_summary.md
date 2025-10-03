# UMD Audit Analysis - Quick Reference Guide

_This is a REFERENCE DOCUMENT ONLY. All actual findings are in the individual notebooks._

---

## 📦 Data Loading Status

**Status:** ✓ Complete - All data loaded and verified (see `01_data_loading.ipynb`)

**Dataset Sizes:**
- Sales Orders: 1,168 records
- Shipments: 1,165 records
- Customer Invoices: 1,167 records
- Customer Master: 73 distributors
- Sales Territory: 5 territories
- Products: 14 product SKUs

**Data Quality:** No critical issues identified. All primary keys unique, referential integrity intact, no missing critical fields.

**Important Data Notes:**
- Sales Orders span 2016-2018 (includes cross-year transactions)
- PaidDate = 9/9/9999 indicates unpaid invoices
- Revenue recognized when goods shipped (InvoiceDate triggers revenue)
- All sales to distributors are final (no refunds/rebates)

---

## 📍 Where to Find Each Answer

| Requirement | Notebook | What It Answers | Status |
|------------|----------|-----------------|--------|
| **Setup** | `01_data_loading.ipynb` | Data loading & quality verification | ✓ Complete |
| **Req 1** | `02_fraud_risk_factors.ipynb` | 3 fraud risk factors | ✓ Complete |
| **Req 2** | `02_reconciliation.ipynb` | How many records = $84.9M revenue & $12M AR? | ✓ Complete |
| **Req 3** | `03_three_way_match.ipynb` | Do orders match shipments match invoices? | ✓ Complete |
| **Req 4** | `04_credit_analysis.ipynb` | Sales without credit limits? | ✓ Complete |
| **Req 5** | `04_credit_analysis.ipynb` | Customers over credit limit? | ✓ Complete |
| **Req 6** | `05_aging_analysis.ipynb` | Aging analysis + allowance adequacy | ✓ Complete |
| **Req 7** | `06_fraud_detection.ipynb` | Additional fraud patterns | ✓ Complete |
| **Req 8** | Based on findings | Who to interview? | Pending |

---

## 📊 Trial Balance Reference

**Values to Reconcile:**
- **Sales Revenue:** $84,867,855
- **Accounts Receivable:** $11,988,886
- **Allowance for Doubtful Accounts:** $315,000

---

## 📝 Case Context Quick Reference

**Key Red Flags from Case Background:**
- Q4 2017: 214% YoY revenue growth (unusual spike)
- SVP has broad authority over sales, training, delivery, customer service
- Aggressive sales targets: "intentionally created at almost unreachable levels"
- Pressure to report strong sales to attract investment capital
- Distributors requested concessions (e.g., holding inventory in UMD's warehouse)
- Sales terms: No refunds or rebates, final sales only

**Audit Assertions at Risk:**
- **Existence/Occurrence** - Did sales really happen?
- **Cutoff** - Were sales recorded in the correct period?
- **Accuracy** - Are amounts correct?
- **Valuation** - Is AR collectible?

**Controls Tested (mixed results at interim):**
1. Three-way match (order → shipment → invoice) - **2 EXCEPTIONS** (unshipped invoices)
2. Credit checks for new customers - **EFFECTIVE** (no exceptions)
3. Sales authorization vs. credit limits - **2 EXCEPTIONS** (customers over limits)
4. Monthly allowance review (>90 days) - **EFFECTIVE** (identification accurate)

---

## 📁 Output Files to Use in Memo

**Tables** (in `outputs/tables/`):
- `revenue_records_2017.csv` - All 1,158 revenue transactions
- `ar_outstanding_12_31_2017.csv` - All 148 AR invoices with payment status
- `reconciliation_summary.csv` - Trial balance reconciliation
- `invoiced_not_shipped.csv` - 2 exceptions (invoiced without shipment)
- `three_way_match_summary.csv` - Three-way match results
- `three_way_match_exceptions.csv` - All 2 exceptions detailed
- `sales_without_credit_limits.csv` - No exceptions found
- `ar_exceeding_credit_limits.csv` - 2 customers exceeding limits (Quad Tech, Shadearts)
- `ar_credit_analysis_full.csv` - Complete AR analysis with 60 customers
- `aging_analysis_full.csv` - Complete aging for all 148 AR invoices
- `aging_over_90_days.csv` - 5 invoices >90 days past due  
- `aging_by_bucket.csv` - Summary by aging bucket
- `aging_unpaid_invoices.csv` - Analysis of 31 still-unpaid invoices
- `client_list_comparison.csv` - Comparison with client's list

**Figures** (in `outputs/figures/`):
- `credit_analysis.png` - Credit utilization and compliance analysis
- `aging_analysis.png` - AR aging distribution and allowance adequacy
- Revenue trends and patterns
- Territory analysis

---

## ✅ Requirements Checklist

- [x] **Setup**: Data loading & quality verification (0 pts - foundational)
- [x] Req 1: Identify 3 fraud risk factors (6 pts)
- [x] Req 2a: Count sales records = $84,867,855 (4 pts)
- [x] Req 2b: Count unpaid invoices = $11,988,886 (4 pts)
- [x] Req 3: Three-way match exceptions (6 pts)
- [x] Req 4: Sales without credit limits (4 pts)
- [x] Req 5: AR exceeding credit limits (6 pts)
- [x] Req 6a: Aging vs. client's list (4 pts)
- [x] Req 6b: Allowance adequacy + concerns (8 pts)
- [x] Req 7a: Plan additional analysis (12 pts)
- [x] Req 7b: Conduct analysis + findings (12 pts)
- [ ] Req 8: Who to interview? (4 pts)

**Total: 70 points**

---

## 🔍 Data Insights (Updated as Analysis Progresses)

### From Data Loading (01_data_loading.ipynb):
- Working with ~1,168 sales transactions across 3 fiscal years
- 73 distributors across 5 territories
- Small product catalog (14 SKUs)
- Close match between orders (1,168), shipments (1,165), and invoices (1,167) suggests most orders completed
- 3 fewer shipments than orders - potential cutoff or incomplete transactions to investigate

### From Reconciliation (02_reconciliation.ipynb):

**Revenue Reconciliation - PERFECT MATCH**
- **1,158 sales records** invoiced in 2017 = $84,867,855 (exact match to trial balance)
- Represents 99.1% of all sales orders in database
- Only 10 orders from database not invoiced in 2017 (likely 2016 or 2018 invoices)
- Q4 2017 revenue: $24.2M (28.6% of annual revenue, 333 transactions)

**AR Reconciliation - PERFECT MATCH (within $0.08)**
- **148 invoice records** outstanding as of 12/31/2017 = $11,988,886
- **Critical finding:** AR composition reveals collection pattern:
  - 31 invoices (21%) still unpaid as of data extraction
  - 117 invoices (79%) paid in early 2018 (but were in AR at year-end)
- Collection rate: 87.2% of 2017 invoices collected by year-end (1,010 of 1,158)
- AR represents 14.1% of annual revenue (relatively high)
- **Data quality improvement:** Reconciliation precision enhanced to show $0.08 variance

**Key Patterns Identified:**
- Q4 revenue concentration needs investigation (potential channel stuffing)
- Most AR invoices paid in January 2018 - could indicate normal 30-day terms OR collection pressure
- 31 invoices remain unpaid - aging analysis required to assess collection risk
- Need to identify which AR invoices (if any) relate to bill-and-hold arrangements mentioned in case

**Red Flags for Further Testing:**
- Bill-and-hold concerns: Case states "Company agreed to hold inventory in their own warehouse"
- If goods weren't delivered, revenue may be improperly recognized
- Q4 spike (214% YoY) concentrated in AR - were distributors pressured to take shipments?

### From Credit Analysis (04_credit_analysis.ipynb):

**Requirement 4 - Sales Without Credit Limits: NO EXCEPTIONS**
- All 1,158 sales transactions in 2017 made to customers with established credit limits
- All 73 distributors have documented credit limits ($50K-$500K range)
- Control #2 (Credit Limit Establishment) appears EFFECTIVE

**Requirement 5 - AR Exceeding Credit Limits: 2 CRITICAL EXCEPTIONS**
- **Quad Tech (CustID 42):** $750,882.73 balance vs $500,000 limit = $250,882.73 over (150.2% utilization)
- **Shadearts (CustID 16):** $496,063.26 balance vs $250,000 limit = $246,063.26 over (198.4% utilization)
- Control #3 (Sales Authorization) **FAILED** - 2 customers (3.3%) exceeding limits
- Combined over-limit exposure: $496,946 (4.1% of total AR balance)

**Critical Concerns - Control Failure:**
- Both over-limit customers received shipments in December 2017 during fraud period
- **Quad Tech:** 6 invoices totaling $750,882.73 (all unpaid)
- **Shadearts:** 6 invoices totaling $496,063.26 (all unpaid)
- Pattern suggests credit limits may have been circumvented during Q4 rush
- **Recommendation:** Investigate whether sales were authorized despite exceeding limits

**Further Testing Needed:**
1. **URGENT:** Investigate credit limit override procedures for Quad Tech and Shadearts
2. Review ModifiedDate field in Customer Master for Q4 2017 limit changes
3. Analyze high-utilization customers for collectibility
4. Compare credit limits 9/30/2017 vs 12/31/2017
5. Interview credit manager about Q4 limit increases and override authorizations
6. Cross-reference over-limit customers with bill-and-hold exceptions
7. Review sales authorization documentation for December 2017 transactions

### From Aging Analysis (05_aging_analysis.ipynb):

**Requirement 6a - Client's List MATCHES Our Analysis:**
- Client's list identified 5 invoices >90 days past due totaling $317,935.92
- Our independent analysis: Exact same 5 invoices, exact same total
- Lists match perfectly - **Control #4 (Monthly Allowance Review) is EFFECTIVE** for identification
- All 5 invoices remain unpaid as of data extraction

**Requirement 6b - Allowance is INADEQUATE:**
- Current allowance: $315,000 (from trial balance)
- >90-day AR balance: $317,935.92
- **Shortfall: $2,935.92** even at 100% reserve on >90-day balances
- Client's methodology appears to assume eventual payment, not 100% reserve

**Critical Findings:**
- **31 invoices totaling $2.6M remain completely unpaid** (no subsequent collection)
- **Two three-way match exceptions ($184K) are unpaid** - goods never shipped, likely disputed
- Only 1 invoice in 61-90 day bucket ($19,275)
- 94.7% of AR is current (0-30 days) - appears very healthy on surface, but unpaid invoices are concern

**Aging Composition:**
- 0-30 days: 138 invoices ($11.3M) - 94.7%
- 31-60 days: 4 invoices ($303K) - 2.5%
- 61-90 days: 1 invoice ($19K) - 0.2%
- >90 days: 5 invoices ($318K) - 2.7%
- Unpaid invoices: 31 invoices ($2.6M) - 22.3%

**Recommended Allowance (Industry Standards):**
- >90 days at 100%: $317,936
- 61-90 days at 50%: $9,638
- Disputed invoices at 100%: $184,025 (three-way match exceptions)
- 31-60 days at 10%: $30,344
- **Total: ~$542K** (vs current $315K = $227K shortfall)

**Audit Implications:**
- Control #4 works for identification but **reserve methodology is inadequate**
- Risk is not control failure but **management judgment** about reserve rates
- In fraud-risk environment, failure to reserve for disputed/unshipped goods is concerning
- Need subsequent events testing on all 31 unpaid invoices
- Need historical write-off data to assess "historically accurate" claim

### From Fraud Detection (06_fraud_detection.ipynb):

**Requirement 7a - Analysis Plan:**
We conducted four targeted analyses to detect fraud patterns:
1. Invoice/shipment timing analysis (bill-and-hold detection)
2. Period-end revenue concentration analysis
3. Territory & customer fraud pattern analysis
4. Credit limit manipulation testing

**Requirement 7b - Key Findings:**

**Finding 1: Period-End Revenue Concentration**
- $1.8M in revenue (2.1% of annual) recorded on December 31 alone (17 transactions)
- Combined with unshipped invoices ($171K), Dec 31 represents $2.0M questionable revenue
- 7 of 17 Dec 31 invoices remain unpaid ($651K, 36% unpaid rate)
- Pattern consistent with aggressive channel stuffing to meet year-end targets

**Finding 2: Suspicious Absence of Bill-and-Hold Evidence**
- ZERO cases found where invoice predated shipment
- Given case mentions distributors requesting to hold inventory, this absence suggests:
  - Data may have been backdated to hide bill-and-hold arrangements
  - Invoices systematically dated to match shipments regardless of actual timing
- Too-clean data is itself a red flag

**Finding 3: Q4 Credit Limit Manipulation**
- 22 distributors (30% of customer base) had credit limits increased in Q4 2017
- Timing coincides with revenue spike
- Explains why Requirements 4 & 5 found "no exceptions" - limits were adjusted to circumvent controls

**Finding 4: High-Risk Customer Exposure**
- 13 distributors have unpaid balances exceeding $50K each
- Concentrated collection risk requiring expanded testing

**Audit Implications:**
- Minimum confirmed revenue overstatement: $171K (unshipped invoices)
- High-risk Dec 31 revenue requiring expanded testing: $1.8M
- Potential total exposure: $171K to $2.0M depending on confirmation results
- Recommend increasing allowance by $350K-500K
- Pattern indicates coordinated management fraud, not isolated errors

**Outputs Generated:**
- period_end_concentration.csv - 17 Dec 31 transactions
- high_risk_customers.csv - 13 high-risk distributors
- q4_credit_limit_changes.csv - Credit limit modifications

### From Three-Way Match (03_three_way_match.ipynb):

**Three-Way Match Results:**
- **1,156 of 1,158** transactions (99.8%) passed three-way match
- **2 CRITICAL EXCEPTIONS** - invoiced but NOT shipped
- Both exceptions on 12/31/2017 (last day of fiscal year)

**Critical Finding - Invoiced but NOT Shipped:**
- **Invoice 101775:** $97,760 - Witchystems - West territory - Unpaid
- **Invoice 101793:** $73,320 - Witchystems - West territory - Unpaid
- **Total improperly recognized revenue:** $171,080 (0.2% of annual revenue)
- **Same customer (Witchystems)** - both transactions to same distributor
- **Both still unpaid** - distributor may be disputing because goods not received

**Audit Implications:**
- **Existence/Occurrence:** FAILED - Revenue recognized without delivery
- **Cutoff:** FAILED - Classic year-end cutoff manipulation
- **Pattern:** Consistent with bill-and-hold fraud OR aggressive year-end invoicing
- **Control failure:** Three-way match control didn't catch these or was overridden

**Required Follow-Up:**
1. Check if goods were shipped in January 2018 (subsequent events)
2. Obtain shipping documentation to confirm non-delivery
3. Interview management about why these were invoiced without shipment
4. Check for similar patterns in prior years
5. If not shipped by audit date, propose $171K revenue adjustment
