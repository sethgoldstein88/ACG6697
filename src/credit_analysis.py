"""
Credit limit analysis for UMD audit project.

This module analyzes credit limits, customer balances, and identifies potential credit violations.
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, Tuple
from .data_loader import UMDDataLoader


class CreditAnalyzer:
    """Class to perform credit limit and balance analysis."""

    def __init__(self, data_loader: UMDDataLoader):
        """
        Initialize the credit analyzer.

        Args:
            data_loader: UMDDataLoader instance with loaded data
        """
        self.loader = data_loader
        self.credit_violations = None
        self.balance_analysis = None

        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )
        self.logger = logging.getLogger(__name__)

    def _validate_and_merge(
        self,
        left_df: pd.DataFrame,
        right_df: pd.DataFrame,
        left_on: str,
        right_on: str = None,
        how: str = "left",
        left_suffix: str = "_left",
        right_suffix: str = "_right",
        merge_threshold: float = 0.8,
    ) -> Tuple[pd.DataFrame, Dict]:
        """
        Perform robust merge with diagnostics and fallback mechanisms.

        Args:
            left_df: Left DataFrame to merge
            right_df: Right DataFrame to merge
            left_on: Column name in left DataFrame for merging
            right_on: Column name in right DataFrame for merging (defaults to left_on)
            how: Type of merge ('left', 'right', 'inner', 'outer')
            left_suffix: Suffix for overlapping columns from left
            right_suffix: Suffix for overlapping columns from right
            merge_threshold: Minimum merge success rate (0-1) to consider successful

        Returns:
            Tuple of (merged DataFrame, diagnostics dict)
        """
        if right_on is None:
            right_on = left_on

        self.logger.info(
            f"Attempting merge on {left_on}={right_on}, left shape: {left_df.shape}, right shape: {right_df.shape}"
        )

        # Pre-merge validation
        left_count = len(left_df)
        right_count = len(right_df)

        if left_count == 0 or right_count == 0:
            self.logger.warning(
                f"Empty DataFrame detected - Left: {left_count}, Right: {right_count}"
            )
            return left_df.assign(
                **{
                    f"{col}{right_suffix}": np.nan
                    for col in right_df.columns
                    if col != right_on
                }
            ), {
                "success": False,
                "merge_rate": 0.0,
                "left_unmatched": left_count,
                "right_unmatched": right_count,
                "error": "Empty DataFrame",
            }

        # Check for key column existence
        if left_on not in left_df.columns:
            self.logger.error(
                f"Left merge column '{left_on}' not found in left DataFrame"
            )
            return left_df.assign(
                **{
                    f"{col}{right_suffix}": np.nan
                    for col in right_df.columns
                    if col != right_on
                }
            ), {
                "success": False,
                "merge_rate": 0.0,
                "left_unmatched": left_count,
                "right_unmatched": right_count,
                "error": f"Missing left column: {left_on}",
            }

        if right_on not in right_df.columns:
            self.logger.error(
                f"Right merge column '{right_on}' not found in right DataFrame"
            )
            return left_df.assign(
                **{
                    f"{col}{right_suffix}": np.nan
                    for col in right_df.columns
                    if col != right_on
                }
            ), {
                "success": False,
                "merge_rate": 0.0,
                "left_unmatched": left_count,
                "right_unmatched": right_count,
                "error": f"Missing right column: {right_on}",
            }

        try:
            # Perform the merge
            merged_df = pd.merge(
                left_df,
                right_df,
                left_on=left_on,
                right_on=right_on,
                how=how,
                suffixes=(left_suffix, right_suffix),
            )

            # Calculate merge diagnostics
            left_matched = (
                merged_df[f"{left_on}{left_suffix}"].notna().sum()
                if f"{left_on}{left_suffix}" in merged_df.columns
                else len(merged_df)
            )
            right_matched = (
                merged_df[right_on].notna().sum()
                if right_on in merged_df.columns
                else len(merged_df)
            )

            merge_rate = left_matched / left_count if left_count > 0 else 0
            left_unmatched = left_count - left_matched
            right_unmatched = right_count - right_matched

            diagnostics = {
                "success": merge_rate >= merge_threshold,
                "merge_rate": merge_rate,
                "left_matched": left_matched,
                "right_matched": right_matched,
                "left_unmatched": left_unmatched,
                "right_unmatched": right_unmatched,
                "merged_shape": merged_df.shape,
                "error": None,
            }

            self.logger.info(
                f"Merge completed - Rate: {merge_rate:.2%}, "
                f"Left unmatched: {left_unmatched}, Right unmatched: {right_unmatched}"
            )

            if merge_rate < merge_threshold:
                self.logger.warning(
                    f"Merge rate {merge_rate:.2%} below threshold {merge_threshold:.2%}"
                )

            return merged_df, diagnostics

        except Exception as e:
            self.logger.error(f"Merge failed with error: {str(e)}")
            return left_df.assign(
                **{
                    f"{col}{right_suffix}": np.nan
                    for col in right_df.columns
                    if col != right_on
                }
            ), {
                "success": False,
                "merge_rate": 0.0,
                "left_unmatched": left_count,
                "right_unmatched": right_count,
                "error": str(e),
            }

    def _preprocess_data(
        self, df: pd.DataFrame, name: str
    ) -> Tuple[pd.DataFrame, Dict]:
        """
        Perform basic data validation checks on DataFrame.

        Args:
            df: DataFrame to validate
            name: Name of the DataFrame for logging

        Returns:
            Tuple of (validated DataFrame, validation results dict)
        """
        self.logger.info(f"Validating {name} DataFrame with shape: {df.shape}")

        validation_results = {
            "total_rows": len(df),
            "null_checks": {},
            "data_type_issues": [],
            "is_valid": True,
        }

        if df.empty:
            self.logger.warning(f"{name} DataFrame is empty")
            validation_results["is_valid"] = False
            return df, validation_results

        # Check for critical columns and their null rates
        critical_columns = ["CustID", "InvoiceID"]  # Common critical columns
        for col in df.columns:
            if col in critical_columns:
                null_rate = df[col].isnull().sum() / len(df)
                validation_results["null_checks"][col] = null_rate
                if null_rate > 0.2:  # More than 20% nulls
                    self.logger.warning(
                        f"High null rate in {name}.{col}: {null_rate:.2%}"
                    )
                    validation_results["is_valid"] = False

        # Check for reasonable credit limits if present
        if "CredLimit" in df.columns:
            zero_limits = (df["CredLimit"] == 0).sum()
            nan_limits = df["CredLimit"].isnull().sum()
            validation_results["null_checks"]["CredLimit_zero"] = zero_limits
            validation_results["null_checks"]["CredLimit_nan"] = nan_limits

            if zero_limits > len(df) * 0.1:  # More than 10% zero limits
                self.logger.warning(
                    f"High rate of zero credit limits in {name}: {zero_limits} ({zero_limits / len(df):.2%})"
                )

        return df, validation_results

    def analyze_credit_limits(self) -> pd.DataFrame:
        """
        Analyze sales to customers without established credit limits.

        Returns:
            DataFrame with credit limit violations
        """
        print("Analyzing credit limits...")
        self.logger.info("Starting credit limit analysis")

        # Get required dataframes
        sales_orders = self.loader.get_dataframe("sales_orders")
        customer_master = self.loader.get_dataframe("customer_master")

        if sales_orders is None or customer_master is None:
            error_msg = "Required dataframes not loaded"
            self.logger.error(error_msg)
            raise ValueError(error_msg)

        # Validate input dataframes
        sales_orders, sales_validation = self._preprocess_data(
            sales_orders, "sales_orders"
        )
        customer_master, master_validation = self._preprocess_data(
            customer_master, "customer_master"
        )

        if not sales_validation["is_valid"]:
            self.logger.warning(
                "Sales orders data validation failed - proceeding with available data"
            )
        if not master_validation["is_valid"]:
            self.logger.warning(
                "Customer master data validation failed - proceeding with available data"
            )

        # Filter for sales with credit approval but no corresponding customer record
        sales_with_credit_approval = sales_orders[
            sales_orders["CredApr"].notna()
        ].copy()
        self.logger.info(
            f"Found {len(sales_with_credit_approval):,} sales with credit approval"
        )

        if sales_with_credit_approval.empty:
            self.logger.warning("No sales with credit approval found")
            return pd.DataFrame(columns=["CustID", "CredLimit", "ViolationType"])

        # Merge with customer master to get credit limits using robust merge
        sales_with_limits, merge_diag = self._validate_and_merge(
            sales_with_credit_approval,
            customer_master[["CustID", "CredLimit"]],
            left_on="CustID",
            how="left",
            merge_threshold=0.8,
        )

        if not merge_diag["success"]:
            self.logger.warning(
                f"Credit limit merge had low success rate ({merge_diag['merge_rate']:.2%}). "
                "This may indicate data quality issues."
            )

        # Find customers without credit limits
        no_credit_limit = sales_with_limits[
            sales_with_limits["CredLimit"].isna()
        ].copy()
        no_credit_limit["ViolationType"] = "No Credit Limit"

        # Find customers with zero credit limits
        zero_credit_limit = sales_with_limits[
            sales_with_limits["CredLimit"] == 0
        ].copy()
        zero_credit_limit["ViolationType"] = "Zero Credit Limit"

        # Combine violations
        credit_violations = pd.concat(
            [no_credit_limit, zero_credit_limit], ignore_index=True
        )

        # Add metadata about data quality
        credit_violations["DataQuality_MergeDiagnostics"] = str(merge_diag)
        credit_violations["DataQuality_SalesValidation"] = str(
            sales_validation["is_valid"]
        )
        credit_violations["DataQuality_MasterValidation"] = str(
            master_validation["is_valid"]
        )

        self.credit_violations = credit_violations

        self.logger.info(f"Found {len(credit_violations):,} credit limit violations")

        # Log violation breakdown
        if len(credit_violations) > 0:
            violation_types = credit_violations["ViolationType"].value_counts()
            self.logger.info(f"Violation breakdown: {dict(violation_types)}")

        return credit_violations

    def analyze_balance_vs_credit_limit(self) -> pd.DataFrame:
        """
        Analyze customer balances against authorized credit limits.

        Returns:
            DataFrame with balance vs credit limit analysis
        """
        print("Analyzing balances vs credit limits...")
        self.logger.info("Starting balance vs credit limit analysis")

        # Get required dataframes
        invoices = self.loader.get_dataframe("customer_invoices")
        customer_master = self.loader.get_dataframe("customer_master")

        if invoices is None or customer_master is None:
            error_msg = "Required dataframes not loaded"
            self.logger.error(error_msg)
            raise ValueError(error_msg)

        # Validate input dataframes
        invoices, invoice_validation = self._preprocess_data(
            invoices, "customer_invoices"
        )
        customer_master, master_validation = self._preprocess_data(
            customer_master, "customer_master"
        )

        if not invoice_validation["is_valid"]:
            self.logger.warning(
                "Invoice data validation failed - proceeding with available data"
            )
        if not master_validation["is_valid"]:
            self.logger.warning(
                "Customer master data validation failed - proceeding with available data"
            )

        # Calculate outstanding balances by customer
        unpaid_invoices = invoices[~invoices["IsPaid"]].copy()
        self.logger.info(f"Found {len(unpaid_invoices):,} unpaid invoices")

        if unpaid_invoices.empty:
            self.logger.warning("No unpaid invoices found - returning empty analysis")
            return pd.DataFrame(
                columns=[
                    "CustID",
                    "InvoiceCount",
                    "TotalBalance",
                    "CredLimit",
                    "CreditUtilization",
                    "ExceedsLimit",
                ]
            )

        # Group by customer and calculate initial balance structure
        customer_balances = (
            unpaid_invoices.groupby("CustID").agg({"InvoiceID": "count"}).reset_index()
        )
        customer_balances.columns = ["CustID", "InvoiceCount"]

        # We need to get the amounts from sales orders since invoices don't have amounts
        sales_orders = self.loader.get_dataframe("sales_orders")
        merge_diagnostics = {}

        if sales_orders is not None:
            # Validate sales orders data
            sales_orders, sales_validation = self._preprocess_data(
                sales_orders, "sales_orders"
            )

            # Get amounts for unpaid invoices using robust merge
            unpaid_with_amounts, merge_diag = self._validate_and_merge(
                unpaid_invoices[["InvoiceID", "CustID"]],
                sales_orders[["InvoiceID", "TotalDue"]].drop_duplicates(),
                left_on="InvoiceID",
                how="left",
                merge_threshold=0.7,  # Allow for some missing matches
            )
            merge_diagnostics["invoice_amount_merge"] = merge_diag

            # Check merge success
            if not merge_diag["success"]:
                self.logger.warning(
                    f"Invoice amount merge had low success rate ({merge_diag['merge_rate']:.2%}). "
                    "Using available data with nulls for missing amounts."
                )

            # Calculate customer balances with amounts
            if "TotalDue" in unpaid_with_amounts.columns:
                customer_balances_with_amounts = (
                    unpaid_with_amounts.groupby("CustID")
                    .agg({"InvoiceID": "count", "TotalDue": "sum"})
                    .reset_index()
                )
                customer_balances_with_amounts.columns = [
                    "CustID",
                    "InvoiceCount",
                    "TotalBalance",
                ]

                # Use amounts data if merge was successful, otherwise fall back to count-only
                if merge_diag["merge_rate"] > 0.5:  # At least 50% success rate
                    customer_balances = customer_balances_with_amounts
                    self.logger.info(
                        f"Successfully calculated balances with amounts for {len(customer_balances):,} customers"
                    )
                else:
                    self.logger.warning(
                        "Using count-only balances due to poor merge rate"
                    )
                    customer_balances["TotalBalance"] = (
                        0  # Default to zero if amounts unavailable
                    )
            else:
                self.logger.warning("TotalDue column not found in merged data")
                customer_balances["TotalBalance"] = 0
        else:
            self.logger.warning(
                "Sales orders not available - using count-only analysis"
            )
            customer_balances["TotalBalance"] = 0
            merge_diagnostics["sales_orders_available"] = False

        # Merge with credit limits using robust merge
        balance_analysis, credit_merge_diag = self._validate_and_merge(
            customer_balances,
            customer_master[["CustID", "CredLimit"]],
            left_on="CustID",
            how="left",
            merge_threshold=0.8,
        )
        merge_diagnostics["credit_limit_merge"] = credit_merge_diag

        # Check merge success and handle missing credit limits
        if not credit_merge_diag["success"]:
            self.logger.warning(
                f"Credit limit merge had low success rate ({credit_merge_diag['merge_rate']:.2%}). "
                "Customers without credit limits will be treated as having zero limits."
            )

        # Fill missing credit limits with 0 (treat as no limit)
        if "CredLimit" not in balance_analysis.columns:
            balance_analysis["CredLimit"] = 0
        else:
            balance_analysis["CredLimit"] = balance_analysis["CredLimit"].fillna(0)

        # Identify credit limit violations
        balance_analysis["CreditUtilization"] = np.where(
            balance_analysis["CredLimit"] > 0,
            balance_analysis.get("TotalBalance", 0) / balance_analysis["CredLimit"],
            0,
        )

        balance_analysis["ExceedsLimit"] = (
            balance_analysis.get("TotalBalance", 0) > balance_analysis["CredLimit"]
        )

        # Add metadata about data quality
        balance_analysis["DataQuality_MergeDiagnostics"] = str(merge_diagnostics)
        balance_analysis["DataQuality_InvoiceValidation"] = str(
            invoice_validation["is_valid"]
        )
        balance_analysis["DataQuality_MasterValidation"] = str(
            master_validation["is_valid"]
        )

        self.balance_analysis = balance_analysis

        violations = balance_analysis[balance_analysis["ExceedsLimit"]]
        self.logger.info(f"Found {len(violations):,} customers exceeding credit limits")

        # Log summary statistics
        total_customers = len(balance_analysis)
        excess_rate = len(violations) / total_customers if total_customers > 0 else 0
        self.logger.info(
            f"Analysis complete: {total_customers:,} customers analyzed, "
            f"{len(violations):,} ({excess_rate:.2%}) exceed limits"
        )

        return balance_analysis

    def get_credit_violation_patterns(self) -> Dict:
        """
        Analyze patterns in credit violations.

        Returns:
            Dictionary with violation patterns and analysis
        """
        patterns = {
            "total_violations": 0,
            "by_territory": {},
            "by_product": {},
            "by_customer": {},
            "risk_factors": [],
            "risk_assessment": "low",
        }

        if self.credit_violations is not None:
            violations = self.credit_violations
            patterns["total_violations"] = len(violations)

            # Analyze by territory
            if "TerritoryID" in violations.columns:
                territory_counts = violations["TerritoryID"].value_counts()
                patterns["by_territory"] = territory_counts.to_dict()

            # Analyze by product
            if "ProdID" in violations.columns:
                product_counts = violations["ProdID"].value_counts()
                patterns["by_product"] = product_counts.to_dict()

            # Analyze by customer
            if "CustID" in violations.columns:
                customer_counts = violations["CustID"].value_counts()
                patterns["by_customer"] = customer_counts.to_dict()

            # Identify risk factors
            if patterns["by_territory"]:
                max_territory = max(
                    patterns["by_territory"], key=patterns["by_territory"].get
                )
                patterns["risk_factors"].append(
                    f"Territory {max_territory} has highest violation rate"
                )

        return patterns

    def get_balance_violation_patterns(self) -> Dict:
        """
        Analyze patterns in balance vs credit limit violations.

        Returns:
            Dictionary with balance violation patterns
        """
        patterns = {
            "total_excess_customers": 0,
            "high_utilization_customers": 0,
            "by_territory": {},
            "risk_assessment": "low",
        }

        if self.balance_analysis is not None:
            balance_df = self.balance_analysis

            # Count violations
            excess_customers = balance_df[balance_df["ExceedsLimit"]]
            patterns["total_excess_customers"] = len(excess_customers)

            # Count high utilization (>80%)
            high_utilization = balance_df[balance_df["CreditUtilization"] > 0.8]
            patterns["high_utilization_customers"] = len(high_utilization)

            # Analyze by territory
            if "TerritoryID" in balance_df.columns:
                territory_excess = excess_customers["TerritoryID"].value_counts()
                patterns["by_territory"] = territory_excess.to_dict()

            # Risk assessment
            total_customers = len(balance_df)
            if total_customers > 0:
                excess_rate = len(excess_customers) / total_customers
                if excess_rate > 0.1:  # 10% of customers exceed limits
                    patterns["risk_assessment"] = "high"
                elif excess_rate > 0.05:  # 5% of customers exceed limits
                    patterns["risk_assessment"] = "moderate"
                else:
                    patterns["risk_assessment"] = "low"

        return patterns


def main():
    """Main function for testing credit analysis."""
    print("UMD Credit Analysis")
    print("=" * 50)

    # Initialize data loader
    loader = UMDDataLoader()
    loader.load_all_files()
    loader.clean_data_types()

    # Initialize analyzer
    analyzer = CreditAnalyzer(loader)

    try:
        # Analyze credit limits
        credit_violations = analyzer.analyze_credit_limits()

        if not credit_violations.empty:
            print("\nCredit Limit Violations Found:")
        print(credit_violations.head())
        print(f"\nTotal violations: {len(credit_violations)}")

        # Get patterns
        credit_patterns = analyzer.get_credit_violation_patterns()
        print("\nCredit Violation Patterns:")
        for territory, count in credit_patterns["by_territory"].items():
            print(f"  Territory {territory}: {count} violations")

        # Analyze balances vs credit limits
        balance_analysis = analyzer.analyze_balance_vs_credit_limit()

        if balance_analysis is not None:
            excess_customers = balance_analysis[balance_analysis["ExceedsLimit"]]
            print(f"\nCustomers Exceeding Credit Limits: {len(excess_customers)}")

            high_utilization = balance_analysis[
                balance_analysis["CreditUtilization"] > 0.8
            ]
            print(f"High Credit Utilization (>80%): {len(high_utilization)}")

            # Get balance patterns
            balance_patterns = analyzer.get_balance_violation_patterns()
            print(
                f"\nBalance Violation Risk Assessment: {balance_patterns['risk_assessment']}"
            )

    except Exception as e:
        print(f"Error in credit analysis: {e}")


if __name__ == "__main__":
    main()
